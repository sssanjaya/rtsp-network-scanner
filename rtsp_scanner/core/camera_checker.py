"""Camera health checker using ffmpeg"""

import subprocess
import shutil
import re
from typing import Dict, Optional


class CameraChecker:
    """Check camera health and stream playability using ffmpeg"""

    def __init__(self, timeout: float = 10.0, logger=None):
        """
        Initialize camera checker

        Args:
            timeout: Timeout for ffmpeg probe in seconds
            logger: Logger instance
        """
        self.timeout = timeout
        self.logger = logger
        self._ffprobe_path = None
        self._ffmpeg_available = None

    def _log(self, message: str, level: str = "info"):
        """Helper to log messages"""
        if self.logger:
            getattr(self.logger, level)(message)

    def is_ffmpeg_available(self) -> bool:
        """Check if ffmpeg/ffprobe is available on the system"""
        if self._ffmpeg_available is not None:
            return self._ffmpeg_available

        self._ffprobe_path = shutil.which('ffprobe')
        self._ffmpeg_available = self._ffprobe_path is not None

        if not self._ffmpeg_available:
            self._log("ffprobe not found in PATH", "warning")

        return self._ffmpeg_available

    def check_stream(self, url: str, username: str = None, password: str = None) -> Dict:
        """
        Check if RTSP stream is working using ffprobe

        Args:
            url: RTSP URL to check
            username: Optional username for authentication
            password: Optional password for authentication

        Returns:
            Dictionary with check results:
            - working: Boolean if stream is accessible and decodable
            - codec: Video codec (e.g., h264, hevc)
            - resolution: Video resolution (e.g., 1920x1080)
            - fps: Frame rate
            - bitrate: Stream bitrate
            - audio_codec: Audio codec if present
            - error: Error message if any
        """
        result = {
            'url': url,
            'working': False,
            'codec': None,
            'resolution': None,
            'fps': None,
            'bitrate': None,
            'audio_codec': None,
            'error': None
        }

        if not self.is_ffmpeg_available():
            result['error'] = "ffprobe not installed"
            return result

        # Build URL with credentials if provided
        if username and password:
            # Parse and reconstruct URL with credentials
            if '://' in url:
                scheme, rest = url.split('://', 1)
                # Remove existing credentials if any
                if '@' in rest:
                    rest = rest.split('@', 1)[1]
                auth_url = f"{scheme}://{username}:{password}@{rest}"
            else:
                auth_url = url
        else:
            auth_url = url

        try:
            # Use ffprobe to get stream info
            cmd = [
                self._ffprobe_path,
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                '-show_format',
                '-rtsp_transport', 'tcp',  # Use TCP for more reliable connection
                '-timeout', str(int(self.timeout * 1000000)),  # Timeout in microseconds
                auth_url
            ]

            self._log(f"Running ffprobe on {url}", "debug")

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout + 5  # Extra buffer for process timeout
            )

            if process.returncode != 0:
                stderr = process.stderr.strip()
                if '401' in stderr or 'Unauthorized' in stderr:
                    result['error'] = "Authentication failed (401)"
                elif '404' in stderr or 'Not Found' in stderr:
                    result['error'] = "Stream not found (404)"
                elif 'Connection refused' in stderr:
                    result['error'] = "Connection refused"
                elif 'timed out' in stderr.lower() or 'timeout' in stderr.lower():
                    result['error'] = "Connection timeout"
                else:
                    result['error'] = stderr[:100] if stderr else "ffprobe failed"
                return result

            # Parse JSON output
            import json
            try:
                data = json.loads(process.stdout)
            except json.JSONDecodeError:
                result['error'] = "Failed to parse ffprobe output"
                return result

            # Extract stream information
            streams = data.get('streams', [])
            format_info = data.get('format', {})

            for stream in streams:
                codec_type = stream.get('codec_type')

                if codec_type == 'video':
                    result['working'] = True
                    result['codec'] = stream.get('codec_name', '').upper()

                    # Get resolution
                    width = stream.get('width')
                    height = stream.get('height')
                    if width and height:
                        result['resolution'] = f"{width}x{height}"

                    # Get frame rate
                    fps_str = stream.get('r_frame_rate', stream.get('avg_frame_rate', ''))
                    if fps_str and '/' in fps_str:
                        try:
                            num, den = fps_str.split('/')
                            if int(den) > 0:
                                fps = int(num) / int(den)
                                result['fps'] = f"{fps:.1f}"
                        except (ValueError, ZeroDivisionError):
                            pass

                    # Get bitrate
                    bitrate = stream.get('bit_rate') or format_info.get('bit_rate')
                    if bitrate:
                        try:
                            bitrate_kbps = int(bitrate) / 1000
                            if bitrate_kbps >= 1000:
                                result['bitrate'] = f"{bitrate_kbps/1000:.1f} Mbps"
                            else:
                                result['bitrate'] = f"{bitrate_kbps:.0f} Kbps"
                        except (ValueError, TypeError):
                            pass

                elif codec_type == 'audio':
                    result['audio_codec'] = stream.get('codec_name', '').upper()

            if result['working']:
                self._log(f"✓ Stream working: {url} ({result['codec']} {result['resolution']})", "debug")
            else:
                result['error'] = "No video stream found"

        except subprocess.TimeoutExpired:
            result['error'] = "ffprobe timeout"
            self._log(f"ffprobe timeout for {url}", "debug")
        except FileNotFoundError:
            result['error'] = "ffprobe not found"
        except Exception as e:
            result['error'] = str(e)[:100]
            self._log(f"Error checking {url}: {e}", "debug")

        return result

    def check_credentials(self, url: str, username: str, password: str) -> Dict:
        """
        Check if credentials are valid by attempting to connect with ffprobe

        Args:
            url: RTSP URL to check
            username: Username to test
            password: Password to test

        Returns:
            Dictionary with:
            - valid: Boolean if credentials work
            - error: Error message if invalid
            - stream_info: Stream details if valid
        """
        result = {
            'url': url,
            'username': username,
            'valid': False,
            'error': None,
            'stream_info': None
        }

        stream_check = self.check_stream(url, username, password)

        if stream_check['working']:
            result['valid'] = True
            result['stream_info'] = {
                'codec': stream_check['codec'],
                'resolution': stream_check['resolution'],
                'fps': stream_check['fps'],
                'bitrate': stream_check['bitrate']
            }
            self._log(f"✓ Credentials valid for {url}")
        else:
            error = stream_check.get('error', '')
            if '401' in str(error) or 'Authentication' in str(error):
                result['error'] = "Invalid credentials"
            else:
                result['error'] = error
            self._log(f"✗ Credentials check failed: {error}")

        return result

    def batch_check(self, channels: list, username: str = None, password: str = None,
                    max_workers: int = 5, progress_callback=None) -> list:
        """
        Check multiple camera streams in parallel

        Args:
            channels: List of channel dicts with 'url' or 'host'/'port'/'path'
            username: Optional username
            password: Optional password
            max_workers: Maximum parallel checks
            progress_callback: Optional callback(checked, total) for progress

        Returns:
            List of check results
        """
        import concurrent.futures

        results = []
        total = len(channels)

        def check_channel(channel):
            # Build URL if not provided
            url = channel.get('url')
            if not url:
                host = channel.get('host')
                port = channel.get('port', 554)
                path = channel.get('path', '/')
                url = f"rtsp://{host}:{port}{path}"

            check_result = self.check_stream(url, username, password)
            # Merge channel info with check result
            return {**channel, **check_result}

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_channel = {executor.submit(check_channel, ch): ch for ch in channels}
            checked = 0

            for future in concurrent.futures.as_completed(future_to_channel):
                result = future.result()
                results.append(result)
                checked += 1
                if progress_callback:
                    progress_callback(checked, total)

        return results
