"""Channel scanner for RTSP cameras"""

import concurrent.futures
from typing import List, Dict
from .rtsp_tester import RTSPTester


class ChannelScanner:
    """Scan for available RTSP channels on cameras"""

    # Common RTSP path patterns for various camera manufacturers
    COMMON_PATHS = [
        # Generic patterns
        "/",
        "/stream",
        "/live",
        "/media",
        "/video",
        "/h264",
        "/mpeg4",
        "/mjpeg",

        # Hikvision
        "/Streaming/Channels/101",
        "/Streaming/Channels/102",
        "/Streaming/Channels/201",
        "/Streaming/Channels/301",
        "/Streaming/Channels/401",
        "/Streaming/Channels/501",
        "/Streaming/Channels/601",
        "/Streaming/Channels/701",
        "/Streaming/Channels/801",
        "/h264/ch1/main/av_stream",
        "/h264/ch1/sub/av_stream",

        # Dahua
        "/cam/realmonitor?channel=1&subtype=0",
        "/cam/realmonitor?channel=1&subtype=1",
        "/cam/realmonitor?channel=2&subtype=0",
        "/cam/realmonitor?channel=3&subtype=0",
        "/cam/realmonitor?channel=4&subtype=0",

        # Axis
        "/axis-media/media.amp",
        "/axis-media/media.amp?videocodec=h264",
        "/axis-media/media.amp?resolution=1920x1080",
        "/mjpg/video.mjpg",

        # Foscam
        "/videoMain",
        "/videoSub",
        "/video.h264",
        "/11",
        "/12",

        # Amcrest
        "/cam/realmonitor?channel=1&subtype=0",
        "/cam/realmonitor?channel=1&subtype=1",

        # TP-Link
        "/stream1",
        "/stream2",
        "/h264_stream",

        # Generic numbered channels
        "/ch01",
        "/ch02",
        "/ch03",
        "/ch04",
        "/channel1",
        "/channel2",
        "/channel3",
        "/channel4",
        "/video1",
        "/video2",
        "/cam1",
        "/cam2",

        # Other common patterns
        "/live/ch00_0",
        "/live/ch00_1",
        "/live/ch01_0",
        "/live.sdp",
        "/av0_0",
        "/av0_1",
        "/onvif1",
        "/onvif2",
        "/profile1",
        "/profile2",
        "/profile3",
    ]

    # Common credential combinations
    COMMON_CREDENTIALS = [
        ('admin', 'admin'),
        ('admin', ''),
        ('admin', '12345'),
        ('admin', 'password'),
        ('admin', '123456'),
        ('root', 'root'),
        ('root', ''),
        ('root', 'pass'),
        ('user', 'user'),
        ('', ''),
    ]

    def __init__(self, timeout: float = 5.0, max_workers: int = 20, logger=None):
        """
        Initialize channel scanner

        Args:
            timeout: Connection timeout in seconds
            max_workers: Maximum number of concurrent workers
            logger: Logger instance
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.logger = logger
        self.tester = RTSPTester(timeout=timeout, logger=logger)

    def _log(self, message: str, level: str = "info"):
        """Helper to log messages"""
        if self.logger:
            getattr(self.logger, level)(message)

    def _detect_stream_type(self, path: str) -> str:
        """
        Detect if the stream is main or sub stream based on path patterns

        Args:
            path: RTSP path

        Returns:
            'Main', 'Sub', or '' (empty string for unknown)
        """
        path_lower = path.lower()

        # Sub stream indicators - check these FIRST (more specific)
        sub_indicators = [
            '/sub/', 'subtype=1', '/streaming/channels/102', '/streaming/channels/202',
            '/streaming/channels/302', '/streaming/channels/402', '/streaming/channels/502',
            '/streaming/channels/602', '/streaming/channels/702', '/streaming/channels/802',
            'videosub', '/stream2', '/ch02', '/channel2', '/video2', '/cam2',
            'resolution=640x480', 'resolution=320x240'
        ]

        # Main stream indicators
        main_indicators = [
            '/main/', 'channel=1&subtype=0', 'subtype=0',
            '/streaming/channels/101', '/streaming/channels/201', '/streaming/channels/301',
            '/streaming/channels/401', '/streaming/channels/501', '/streaming/channels/601',
            '/streaming/channels/701', '/streaming/channels/801',
            'videomain', '/stream1', '/ch01', '/channel1', '/video1', '/cam1',
            'resolution=1920x1080', 'resolution=1280x720'
        ]

        # Check for sub stream first (more specific patterns)
        for indicator in sub_indicators:
            if indicator in path_lower:
                return 'Sub'

        # Check for main stream
        for indicator in main_indicators:
            if indicator in path_lower:
                return 'Main'

        return ''

    def scan_channels(self, host: str, port: int = 554,
                     username: str = None, password: str = None,
                     custom_paths: List[str] = None) -> List[Dict]:
        """
        Scan for available RTSP channels on a host

        Args:
            host: Target host IP or hostname
            port: RTSP port (default: 554)
            username: Optional username for authentication
            password: Optional password for authentication
            custom_paths: Optional list of custom paths to test

        Returns:
            List of available channels with details
        """
        paths_to_test = custom_paths if custom_paths else self.COMMON_PATHS

        self._log(f"Scanning {len(paths_to_test)} channel paths on {host}:{port}")

        available_channels = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            for path in paths_to_test:
                url = self.tester.generate_rtsp_url(host, port, path, username, password)
                futures.append(executor.submit(self._test_channel, url, path))

            completed = 0
            total = len(futures)

            for future in concurrent.futures.as_completed(futures):
                completed += 1
                if completed % 10 == 0:
                    self._log(f"Progress: {completed}/{total} channels tested", "debug")

                result = future.result()
                if result:
                    available_channels.append(result)

        self._log(f"Found {len(available_channels)} available channel(s)")
        return available_channels

    def _test_channel(self, url: str, path: str) -> Dict:
        """
        Test a single channel path

        Args:
            url: Complete RTSP URL to test
            path: Path being tested

        Returns:
            Channel info dict if available, None otherwise
        """
        self._log(f"Testing channel: {path}", "debug")

        result = self.tester.test_rtsp_connection(url)

        if result['reachable'] and result.get('status_code') in [200, 401]:
            stream_type = self._detect_stream_type(path)
            channel_info = {
                'url': url,
                'path': path,
                'status_code': result['status_code'],
                'response_time': result['response_time'],
                'stream_type': stream_type,
                'server_info': result.get('server_info'),
                'requires_auth': result['status_code'] == 401
            }

            self._log(f"Found available channel: {path} (Status: {result['status_code']})")
            return channel_info

        return None

    def scan_with_credentials(self, host: str, port: int = 554,
                            custom_paths: List[str] = None,
                            custom_credentials: List[tuple] = None) -> List[Dict]:
        """
        Scan channels trying multiple credential combinations

        Args:
            host: Target host IP or hostname
            port: RTSP port (default: 554)
            custom_paths: Optional list of custom paths to test
            custom_credentials: Optional list of (username, password) tuples

        Returns:
            List of available channels with working credentials
        """
        paths_to_test = custom_paths if custom_paths else self.COMMON_PATHS[:20]  # Limit paths
        credentials_to_test = custom_credentials if custom_credentials else self.COMMON_CREDENTIALS

        self._log(f"Scanning with {len(credentials_to_test)} credential combinations "
                 f"and {len(paths_to_test)} paths")

        available_channels = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            for username, password in credentials_to_test:
                for path in paths_to_test:
                    url = self.tester.generate_rtsp_url(host, port, path, username, password)
                    futures.append(executor.submit(
                        self._test_channel_with_creds, url, path, username, password
                    ))

            completed = 0
            total = len(futures)

            for future in concurrent.futures.as_completed(futures):
                completed += 1
                if completed % 20 == 0:
                    self._log(f"Progress: {completed}/{total} combinations tested", "debug")

                result = future.result()
                if result:
                    available_channels.append(result)

        self._log(f"Found {len(available_channels)} working channel/credential combination(s)")
        return available_channels

    def _test_channel_with_creds(self, url: str, path: str,
                                 username: str, password: str) -> Dict:
        """
        Test a channel with specific credentials

        Args:
            url: Complete RTSP URL to test
            path: Path being tested
            username: Username for authentication
            password: Password for authentication

        Returns:
            Channel info dict if accessible, None otherwise
        """
        self._log(f"Testing {path} with user={username}", "debug")

        result = self.tester.test_rtsp_connection(url)

        if result['reachable'] and result.get('status_code') == 200:
            channel_info = {
                'url': url,
                'path': path,
                'username': username,
                'password': password,
                'status_code': result['status_code'],
                'response_time': result['response_time'],
                'server_info': result.get('server_info')
            }

            self._log(f"Success: {path} with {username}:{password}")
            return channel_info

        return None

    def scan_numbered_channels(self, host: str, port: int = 554,
                              channel_range: range = range(1, 17),
                              username: str = None, password: str = None) -> List[Dict]:
        """
        Scan numbered channels (e.g., /channel1, /channel2, etc.)

        Args:
            host: Target host IP or hostname
            port: RTSP port (default: 554)
            channel_range: Range of channel numbers to test
            username: Optional username for authentication
            password: Optional password for authentication

        Returns:
            List of available numbered channels
        """
        patterns = [
            "/channel{}",
            "/ch{}",
            "/ch0{}",
            "/video{}",
            "/cam{}",
            "/stream{}",
            "/Streaming/Channels/{}01",
        ]

        paths = []
        for num in channel_range:
            for pattern in patterns:
                if '0{}' in pattern and num < 10:
                    paths.append(pattern.format(num))
                else:
                    paths.append(pattern.format(num))

        self._log(f"Scanning {len(paths)} numbered channel variations")
        return self.scan_channels(host, port, username, password, paths)

    def quick_scan(self, host: str, port: int = 554) -> List[Dict]:
        """
        Perform a quick scan with most common paths only

        Args:
            host: Target host IP or hostname
            port: RTSP port (default: 554)

        Returns:
            List of available channels
        """
        quick_paths = [
            "/",
            "/stream",
            "/live",
            "/Streaming/Channels/101",
            "/Streaming/Channels/102",
            "/cam/realmonitor?channel=1&subtype=0",
            "/axis-media/media.amp",
            "/videoMain",
            "/h264/ch1/main/av_stream",
            "/channel1",
        ]

        self._log(f"Quick scan on {host}:{port}")
        return self.scan_channels(host, port, custom_paths=quick_paths)
