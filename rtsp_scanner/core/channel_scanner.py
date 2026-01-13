"""Channel scanner for RTSP cameras"""

import concurrent.futures
import re
import sys
import threading
from typing import List, Dict
from .rtsp_tester import RTSPTester


class ProgressBar:
    """Simple thread-safe progress bar for terminal output"""

    def __init__(self, total: int, prefix: str = "", width: int = 40):
        """
        Initialize progress bar

        Args:
            total: Total number of items
            prefix: Prefix text to show before progress bar
            width: Width of the progress bar in characters
        """
        self.total = total
        self.prefix = prefix
        self.width = width
        self.current = 0
        self.found = 0
        self._lock = threading.Lock()
        self._last_line_length = 0

    def update(self, increment: int = 1, found: bool = False):
        """Update progress bar"""
        with self._lock:
            self.current += increment
            if found:
                self.found += 1
            self._render()

    def _render(self):
        """Render the progress bar to terminal"""
        if self.total == 0:
            return

        percent = self.current / self.total
        filled = int(self.width * percent)
        bar = "█" * filled + "░" * (self.width - filled)

        line = f"\r{self.prefix} [{bar}] {self.current}/{self.total} ({self.found} found)"

        # Clear any extra characters from previous line
        if len(line) < self._last_line_length:
            line += " " * (self._last_line_length - len(line))
        self._last_line_length = len(line)

        sys.stdout.write(line)
        sys.stdout.flush()

    def finish(self):
        """Finish the progress bar and move to new line"""
        sys.stdout.write("\n")
        sys.stdout.flush()


class ChannelScanner:
    """Scan for available RTSP channels on cameras"""

    # Common RTSP path patterns for various camera manufacturers
    COMMON_PATHS = [
        # Generic patterns (most common first)
        "/",
        "/stream",
        "/stream1",
        "/stream2",
        "/live",
        "/live.sdp",
        "/video",
        "/media",
        "/h264",

        # Hikvision - All 8 channels with main (x01) and sub (x02) streams
        "/Streaming/Channels/101",
        "/Streaming/Channels/102",
        "/Streaming/Channels/201",
        "/Streaming/Channels/202",
        "/Streaming/Channels/301",
        "/Streaming/Channels/302",
        "/Streaming/Channels/401",
        "/Streaming/Channels/402",
        "/Streaming/Channels/501",
        "/Streaming/Channels/502",
        "/Streaming/Channels/601",
        "/Streaming/Channels/602",
        "/Streaming/Channels/701",
        "/Streaming/Channels/702",
        "/Streaming/Channels/801",
        "/Streaming/Channels/802",
        "/h264/ch1/main/av_stream",
        "/h264/ch1/sub/av_stream",
        "/h264/ch2/main/av_stream",
        "/h264/ch2/sub/av_stream",

        # Dahua / Amcrest - Multiple channels
        "/cam/realmonitor?channel=1&subtype=0",
        "/cam/realmonitor?channel=1&subtype=1",
        "/cam/realmonitor?channel=2&subtype=0",
        "/cam/realmonitor?channel=2&subtype=1",
        "/cam/realmonitor?channel=3&subtype=0",
        "/cam/realmonitor?channel=4&subtype=0",

        # Generic numbered channels
        "/ch01",
        "/ch02",
        "/ch03",
        "/ch04",
        "/channel1",
        "/channel2",
        "/video1",
        "/video2",

        # Axis
        "/axis-media/media.amp",
        "/mjpg/video.mjpg",

        # Foscam
        "/videoMain",
        "/videoSub",
        "/11",
        "/12",

        # Other common patterns
        "/live/ch00_0",
        "/live/ch01_0",
        "/av0_0",
        "/onvif1",
        "/profile1",
        "/profile2",

        # Additional patterns
        "/MediaInput/h264",
        "/play1.sdp",
        "/1/stream1",
        "/0/video0",
        "/streaming/channels/1",
    ]

    # HTTP camera paths (for port 8080 and similar)
    HTTP_CAMERA_PATHS = [
        # XMEye / generic Chinese DVR/NVR
        "/h264_stream",
        "/mjpegstream.cgi",
        "/cgi-bin/snapshot.cgi",
        "/video.mjpg",
        "/videostream.cgi",
        "/live/0/h264.sdp",
        "/live/1/h264.sdp",
        "/ipcam/stream.cgi",
        "/live_mpeg4.sdp",
        "/nphMoticonJpeg?Resolution=640x480&Quality=Clarity",
        "/GetData.cgi",
        "/image/jpeg.cgi",
        "/video.cgi",

        # Wanscam / generic IP cameras
        "/videostream.asf?usr=admin&pwd=",
        "/video.mjpg",
        "/mjpg/video.mjpg",

        # Generic ONVIF
        "/onvif/device_service",
        "/onvif/media",
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

    # Invalid path used to detect permissive servers
    INVALID_TEST_PATH = "/thispathshouldnotexist99999"

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

    def _is_permissive_server(self, host: str, port: int, username: str = None, password: str = None) -> bool:
        """
        Check if server accepts any path (permissive server detection).
        A permissive server returns 200/401 for invalid paths.

        Args:
            host: Target host
            port: Target port
            username: Optional username
            password: Optional password

        Returns:
            True if server is permissive, False if strict
        """
        url = self.tester.generate_rtsp_url(host, port, self.INVALID_TEST_PATH, username, password)
        result = self.tester.test_rtsp_connection(url)

        # If invalid path gets 200 or 401, server is permissive
        if result.get('status_code') in [200, 401]:
            self._log(f"Permissive server detected at {host}:{port} (accepts invalid paths)", "debug")
            return True

        # If we get 404 or other error, server is strict
        self._log(f"Strict server at {host}:{port} (rejects invalid paths)", "debug")
        return False

    def check_rtsp_protocol(self, host: str, port: int) -> bool:
        """
        Check if a host:port is speaking RTSP protocol

        Args:
            host: Target host IP or hostname
            port: Target port

        Returns:
            True if RTSP protocol is detected, False otherwise
        """
        result = self.tester.check_rtsp_protocol(host, port)
        return result.get('is_rtsp', False)

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

        # Hikvision pattern: x01 = main, x02 = sub (e.g., 101, 201, 301... are main; 102, 202, 302... are sub)
        hikvision_match = re.search(r'/streaming/channels/(\d)0(\d)', path_lower)
        if hikvision_match:
            stream_num = hikvision_match.group(2)
            if stream_num == '1':
                return 'Main'
            elif stream_num == '2':
                return 'Sub'

        # Sub stream indicators - check these FIRST (more specific)
        sub_indicators = [
            '/sub/', 'subtype=1',
            'videosub', '/stream2', '/ch02', '/channel2', '/video2', '/cam2',
            'resolution=640x480', 'resolution=320x240'
        ]

        # Main stream indicators
        main_indicators = [
            '/main/', 'channel=1&subtype=0', 'subtype=0',
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
                     custom_paths: List[str] = None,
                     show_progress: bool = True) -> List[Dict]:
        """
        Scan for available RTSP channels on a host

        Args:
            host: Target host IP or hostname
            port: RTSP port (default: 554)
            username: Optional username for authentication
            password: Optional password for authentication
            custom_paths: Optional list of custom paths to test
            show_progress: Show progress bar (default: True)

        Returns:
            List of available channels with details
        """
        paths_to_test = custom_paths if custom_paths else self.COMMON_PATHS
        total = len(paths_to_test)

        # First, detect if server is permissive (accepts any path)
        is_permissive = self._is_permissive_server(host, port, username, password)

        self._log(f"Scanning {total} channel paths on {host}:{port} (permissive={is_permissive})", "debug")

        available_channels = []

        # Create progress bar
        progress = ProgressBar(total, prefix=f"Scanning {host}:{port}") if show_progress else None

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            for path in paths_to_test:
                url = self.tester.generate_rtsp_url(host, port, path, username, password)
                futures.append(executor.submit(self._test_channel, url, path, is_permissive))

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                found = False
                if result:
                    available_channels.append(result)
                    found = True

                if progress:
                    progress.update(found=found)

        if progress:
            progress.finish()

        self._log(f"Found {len(available_channels)} available channel(s) on {host}:{port}")
        return available_channels

    def _test_channel(self, url: str, path: str, is_permissive: bool = False) -> Dict:
        """
        Test a single channel path

        Args:
            url: Complete RTSP URL to test
            path: Path being tested
            is_permissive: Whether the server accepts any path

        Returns:
            Channel info dict if available, None otherwise
        """
        result = self.tester.test_rtsp_connection(url)
        status_code = result.get('status_code')

        # For permissive servers: only accept 200 with valid SDP
        # For strict servers: accept 200 with SDP or 401 (auth required)
        is_valid = False

        if status_code == 200 and result.get('has_valid_sdp'):
            # Valid stream with SDP content
            is_valid = True
        elif status_code == 401 and not is_permissive:
            # Auth required - valid only for strict servers
            # (permissive servers return 401 for everything)
            is_valid = True

        if is_valid:
            stream_type = self._detect_stream_type(path)
            channel_info = {
                'url': url,
                'path': path,
                'status_code': status_code,
                'response_time': result['response_time'],
                'stream_type': stream_type,
                'codec': result.get('codec'),
                'resolution': result.get('resolution'),
                'server_info': result.get('server_info'),
                'requires_auth': status_code == 401
            }

            self._log(f"Found channel: {path} (Status: {status_code})", "debug")
            return channel_info

        return None

    def scan_with_credentials(self, host: str, port: int = 554,
                            custom_paths: List[str] = None,
                            custom_credentials: List[tuple] = None,
                            show_progress: bool = True) -> List[Dict]:
        """
        Scan channels trying multiple credential combinations

        Args:
            host: Target host IP or hostname
            port: RTSP port (default: 554)
            custom_paths: Optional list of custom paths to test
            custom_credentials: Optional list of (username, password) tuples
            show_progress: Show progress bar (default: True)

        Returns:
            List of available channels with working credentials
        """
        paths_to_test = custom_paths if custom_paths else self.COMMON_PATHS[:20]  # Limit paths
        credentials_to_test = custom_credentials if custom_credentials else self.COMMON_CREDENTIALS

        total = len(credentials_to_test) * len(paths_to_test)
        self._log(f"Scanning with {len(credentials_to_test)} credentials × {len(paths_to_test)} paths", "debug")

        available_channels = []

        # Create progress bar
        progress = ProgressBar(total, prefix=f"Auth scan {host}:{port}") if show_progress else None

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            for username, password in credentials_to_test:
                for path in paths_to_test:
                    url = self.tester.generate_rtsp_url(host, port, path, username, password)
                    futures.append(executor.submit(
                        self._test_channel_with_creds, url, path, username, password
                    ))

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                found = False
                if result:
                    available_channels.append(result)
                    found = True

                if progress:
                    progress.update(found=found)

        if progress:
            progress.finish()

        self._log(f"Found {len(available_channels)} working channel/credential combination(s) on {host}:{port}")
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

            self._log(f"Success: {path} with {username}:{password}", "debug")
            return channel_info

        return None

    def scan_numbered_channels(self, host: str, port: int = 554,
                              channel_range: range = range(1, 17),
                              username: str = None, password: str = None,
                              show_progress: bool = True) -> List[Dict]:
        """
        Scan numbered channels (e.g., /channel1, /channel2, etc.)

        Args:
            host: Target host IP or hostname
            port: RTSP port (default: 554)
            channel_range: Range of channel numbers to test
            username: Optional username for authentication
            password: Optional password for authentication
            show_progress: Show progress bar (default: True)

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

        self._log(f"Scanning {len(paths)} numbered channel variations", "debug")
        return self.scan_channels(host, port, username, password, paths, show_progress)

    def quick_scan(self, host: str, port: int = 554, show_progress: bool = True) -> List[Dict]:
        """
        Perform a quick scan with most common paths only

        Args:
            host: Target host IP or hostname
            port: RTSP port (default: 554)
            show_progress: Show progress bar (default: True)

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

        self._log(f"Quick scan on {host}:{port}", "debug")
        return self.scan_channels(host, port, custom_paths=quick_paths, show_progress=show_progress)
