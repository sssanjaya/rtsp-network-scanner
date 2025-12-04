"""RTSP URL validator and tester"""

import socket
import re
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
import time


class RTSPTester:
    """Test and validate RTSP URLs"""

    def __init__(self, timeout: float = 5.0, logger=None):
        """
        Initialize RTSP tester

        Args:
            timeout: Connection timeout in seconds
            logger: Logger instance
        """
        self.timeout = timeout
        self.logger = logger
        self.common_credentials = [
            ('admin', 'admin'),
            ('admin', ''),
            ('admin', '12345'),
            ('admin', 'password'),
            ('root', 'root'),
            ('root', ''),
            ('', ''),
        ]

    # Known camera manufacturers by server header patterns
    CAMERA_MANUFACTURERS = {
        'hikvision': ['hikvision', 'hik', 'dvr', 'nvr', 'ipc'],
        'dahua': ['dahua', 'dh-', 'ipc-'],
        'axis': ['axis', 'vapix'],
        'foscam': ['foscam', 'ipcam'],
        'amcrest': ['amcrest'],
        'reolink': ['reolink'],
        'uniview': ['uniview', 'unv'],
        'hanwha': ['hanwha', 'samsung', 'wisenet'],
        'vivotek': ['vivotek'],
        'geovision': ['geovision', 'gv-'],
        'bosch': ['bosch'],
        'honeywell': ['honeywell'],
        'pelco': ['pelco'],
        'panasonic': ['panasonic'],
        'sony': ['sony'],
        'ubiquiti': ['ubiquiti', 'ubnt', 'unifi'],
        'tp-link': ['tp-link', 'tapo'],
        'wyze': ['wyze'],
        'eufy': ['eufy', 'anker'],
    }

    def _detect_manufacturer(self, server_info: str) -> str:
        """Detect camera manufacturer from server header"""
        if not server_info:
            return None
        server_lower = server_info.lower()
        for manufacturer, patterns in self.CAMERA_MANUFACTURERS.items():
            for pattern in patterns:
                if pattern in server_lower:
                    return manufacturer.title()
        return None

    def check_rtsp_protocol(self, host: str, port: int) -> Dict:
        """
        Check if a host:port is speaking RTSP protocol by sending OPTIONS request

        Args:
            host: Target host IP or hostname
            port: Target port

        Returns:
            Dictionary with protocol check results including:
            - is_rtsp: Boolean if RTSP protocol is detected
            - server_info: Server header if available
            - manufacturer: Detected camera manufacturer
            - supported_methods: RTSP methods supported
            - error: Error message if any
        """
        result = {
            'host': host,
            'port': port,
            'is_rtsp': False,
            'server_info': None,
            'manufacturer': None,
            'supported_methods': None,
            'error': None
        }

        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((host, port))

            # Send RTSP OPTIONS request (simplest RTSP request)
            request = (
                f"OPTIONS rtsp://{host}:{port}/ RTSP/1.0\r\n"
                f"CSeq: 1\r\n"
                f"User-Agent: RTSP-Scanner/2.4\r\n"
                f"\r\n"
            )
            sock.sendall(request.encode())

            response = sock.recv(2048).decode('utf-8', errors='ignore')

            # Check if response looks like RTSP
            if response.startswith('RTSP/'):
                result['is_rtsp'] = True

                # Parse response headers
                for line in response.split('\r\n'):
                    line_lower = line.lower()
                    if line_lower.startswith('server:'):
                        result['server_info'] = line.split(':', 1)[1].strip()
                        result['manufacturer'] = self._detect_manufacturer(result['server_info'])
                    elif line_lower.startswith('public:'):
                        # Extract supported methods
                        methods = line.split(':', 1)[1].strip()
                        result['supported_methods'] = [m.strip() for m in methods.split(',')]

                self._log(f"RTSP protocol detected on {host}:{port}", "debug")
            else:
                result['error'] = "Not RTSP protocol"
                self._log(f"Non-RTSP response from {host}:{port}", "debug")

        except socket.timeout:
            result['error'] = "Connection timeout"
        except socket.error as e:
            result['error'] = f"Socket error: {str(e)}"
        except Exception as e:
            result['error'] = f"Error: {str(e)}"
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass

        return result

    def _log(self, message: str, level: str = "info"):
        """Helper to log messages"""
        if self.logger:
            getattr(self.logger, level)(message)

    def _parse_sdp(self, sdp_lines: list) -> dict:
        """
        Parse SDP data to extract codec and resolution

        Args:
            sdp_lines: List of SDP lines

        Returns:
            Dictionary with codec and resolution info
        """
        info = {
            'codec': None,
            'resolution': None
        }

        sdp_text = '\n'.join(sdp_lines)

        # Extract video codec from rtpmap
        # Example: a=rtpmap:96 H264/90000
        codec_match = re.search(r'a=rtpmap:\d+\s+(\w+)/\d+', sdp_text, re.IGNORECASE)
        if codec_match:
            codec = codec_match.group(1).upper()
            # Normalize codec names
            if codec in ['H264', 'H.264']:
                info['codec'] = 'H.264'
            elif codec in ['H265', 'H.265', 'HEVC']:
                info['codec'] = 'H.265'
            elif codec in ['MJPEG', 'JPEG']:
                info['codec'] = 'MJPEG'
            elif codec in ['MPEG4']:
                info['codec'] = 'MPEG4'
            else:
                info['codec'] = codec

        # Extract resolution from fmtp or other attributes
        # Example: a=fmtp:96 ... x-dimensions=1920,1080
        # or a=framesize:96 1920-1080
        res_patterns = [
            r'x-dimensions=(\d+),(\d+)',
            r'framesize:\d+\s+(\d+)-(\d+)',
            r'resolution[:\s]+(\d+)x(\d+)',
            r'width[:\s]*=\s*(\d+).*height[:\s]*=\s*(\d+)'
        ]

        for pattern in res_patterns:
            res_match = re.search(pattern, sdp_text, re.IGNORECASE)
            if res_match:
                width = res_match.group(1)
                height = res_match.group(2)
                info['resolution'] = f"{width}x{height}"
                break

        return info

    def validate_rtsp_url(self, url: str) -> Tuple[bool, str]:
        """
        Validate RTSP URL format

        Args:
            url: RTSP URL to validate

        Returns:
            Tuple of (is_valid, message)
        """
        self._log(f"Validating RTSP URL: {url}", "debug")

        if not url:
            return False, "URL is empty"

        if not url.startswith('rtsp://'):
            return False, "URL must start with 'rtsp://'"

        try:
            parsed = urlparse(url)

            if not parsed.hostname:
                return False, "Missing hostname"

            # Validate hostname (IP or domain)
            hostname = parsed.hostname
            if not self._is_valid_hostname(hostname):
                return False, f"Invalid hostname: {hostname}"

            # Validate port if present
            if parsed.port and (parsed.port < 1 or parsed.port > 65535):
                return False, f"Invalid port: {parsed.port}"

            self._log(f"URL validation passed: {url}", "debug")
            return True, "Valid RTSP URL"

        except Exception as e:
            return False, f"Invalid URL format: {str(e)}"

    def _is_valid_hostname(self, hostname: str) -> bool:
        """Check if hostname is valid IP or domain"""
        # Check if it's a valid IP
        try:
            socket.inet_aton(hostname)
            return True
        except socket.error:
            pass

        # Check if it's a valid domain name
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        )
        return bool(domain_pattern.match(hostname))

    def parse_rtsp_url(self, url: str) -> Optional[Dict]:
        """
        Parse RTSP URL into components

        Args:
            url: RTSP URL to parse

        Returns:
            Dictionary with URL components or None if invalid
        """
        is_valid, message = self.validate_rtsp_url(url)
        if not is_valid:
            self._log(f"Invalid URL: {message}", "error")
            return None

        try:
            parsed = urlparse(url)
            return {
                'scheme': parsed.scheme,
                'hostname': parsed.hostname,
                'port': parsed.port or 554,
                'path': parsed.path or '/',
                'username': parsed.username,
                'password': parsed.password,
                'full_url': url
            }
        except Exception as e:
            self._log(f"Error parsing URL: {str(e)}", "error")
            return None

    def test_rtsp_connection(self, url: str, verbose: bool = False) -> Dict:
        """
        Test RTSP connection by sending DESCRIBE request

        Args:
            url: RTSP URL to test
            verbose: If True, log connection attempts (default: False)

        Returns:
            Dictionary with test results
        """
        if verbose:
            self._log(f"Testing RTSP connection: {url}")

        result = {
            'url': url,
            'reachable': False,
            'response_time': None,
            'status_code': None,
            'server_info': None,
            'error': None
        }

        parsed = self.parse_rtsp_url(url)
        if not parsed:
            result['error'] = "Invalid URL"
            return result

        host = parsed['hostname']
        port = parsed['port']

        start_time = time.time()
        sock = None

        try:
            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)

            self._log(f"Connecting to {host}:{port}", "debug")
            sock.connect((host, port))

            # Send RTSP DESCRIBE request
            request = (
                f"DESCRIBE {url} RTSP/1.0\r\n"
                f"CSeq: 1\r\n"
                f"User-Agent: RTSP-Scanner/2.4\r\n"
                f"Accept: application/sdp\r\n"
                f"\r\n"
            )

            self._log(f"Sending DESCRIBE request", "debug")
            sock.sendall(request.encode())

            # Receive response
            response = sock.recv(4096).decode('utf-8', errors='ignore')
            response_time = time.time() - start_time

            self._log(f"Received response in {response_time:.3f}s", "debug")

            # Parse response
            lines = response.split('\r\n')
            if lines:
                status_line = lines[0]
                self._log(f"Status line: {status_line}", "debug")

                # Extract status code
                match = re.match(r'RTSP/\d\.\d\s+(\d+)', status_line)
                if match:
                    status_code = int(match.group(1))
                    result['status_code'] = status_code
                    result['response_time'] = response_time

                    # Extract server info, content-length and SDP data
                    sdp_data = []
                    in_sdp = False
                    content_length = 0
                    has_sdp_content_type = False
                    for line in lines:
                        if line.lower().startswith('server:'):
                            result['server_info'] = line.split(':', 1)[1].strip()
                            # Detect manufacturer from server header
                            result['manufacturer'] = self._detect_manufacturer(result['server_info'])
                        if line.lower().startswith('content-length:'):
                            try:
                                content_length = int(line.split(':', 1)[1].strip())
                            except ValueError:
                                pass
                        if line.lower().startswith('content-type:') and 'sdp' in line.lower():
                            has_sdp_content_type = True
                            in_sdp = True
                        elif in_sdp and line.strip():
                            sdp_data.append(line)

                    # For 200 OK, validate that we have actual SDP content
                    if status_code == 200:
                        # Check for valid SDP: must have content-type: application/sdp
                        # and actual SDP data (v=, m=, etc.)
                        has_valid_sdp = False
                        if has_sdp_content_type and sdp_data:
                            # Look for essential SDP fields
                            sdp_text = '\n'.join(sdp_data)
                            if 'v=' in sdp_text or 'm=' in sdp_text or 'a=rtpmap' in sdp_text:
                                has_valid_sdp = True
                                codec_info = self._parse_sdp(sdp_data)
                                result.update(codec_info)

                        if has_valid_sdp:
                            result['reachable'] = True
                            result['has_valid_sdp'] = True
                            self._log(f"RTSP stream found: {url}", "debug")
                        else:
                            # 200 but no valid SDP - server accepts anything
                            result['reachable'] = False
                            result['has_valid_sdp'] = False
                            result['error'] = "No valid SDP content"
                            self._log(f"RTSP 200 but no valid SDP: {url}", "debug")

                    elif status_code == 401:
                        # 401 means path exists but needs auth
                        result['reachable'] = True
                        self._log(f"RTSP requires authentication: {url}", "debug")
                        result['error'] = "Authentication required"
                    elif status_code == 404:
                        result['reachable'] = False
                        self._log(f"RTSP path not found: {url}", "debug")
                        result['error'] = "Path not found"
                    else:
                        result['reachable'] = False
                        result['error'] = f"Status code: {status_code}"
                else:
                    result['error'] = "Invalid RTSP response"

        except socket.timeout:
            result['error'] = "Connection timeout"
            result['response_time'] = time.time() - start_time
            self._log(f"Connection timeout for {url}", "debug")
        except socket.error as e:
            result['error'] = f"Socket error: {str(e)}"
            result['response_time'] = time.time() - start_time
            self._log(f"Socket error for {url}: {str(e)}", "debug")
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
            result['response_time'] = time.time() - start_time
            self._log(f"Error testing {url}: {str(e)}", "debug")
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass

        return result

    def test_rtsp_with_auth(self, url: str, username: str, password: str) -> Dict:
        """
        Test RTSP connection with authentication

        Args:
            url: RTSP URL to test
            username: Username for authentication
            password: Password for authentication

        Returns:
            Dictionary with test results
        """
        # Parse URL and inject credentials
        parsed = self.parse_rtsp_url(url)
        if not parsed:
            return {'url': url, 'reachable': False, 'error': 'Invalid URL'}

        # Construct URL with credentials
        scheme = parsed['scheme']
        host = parsed['hostname']
        port = parsed['port']
        path = parsed['path']

        if username or password:
            auth_url = f"{scheme}://{username}:{password}@{host}:{port}{path}"
        else:
            auth_url = url

        self._log(f"Testing with auth - user: {username}", "debug")
        return self.test_rtsp_connection(auth_url)

    def test_common_credentials(self, url: str) -> list:
        """
        Test RTSP URL with common credentials

        Args:
            url: RTSP URL to test

        Returns:
            List of successful credential combinations
        """
        self._log(f"Testing common credentials for: {url}")

        successful = []

        for username, password in self.common_credentials:
            self._log(f"Trying credentials - user: '{username}', pass: '{password}'", "debug")
            result = self.test_rtsp_with_auth(url, username, password)

            if result['reachable'] and result.get('status_code') == 200:
                self._log(f"Success with credentials - user: '{username}', pass: '{password}'")
                successful.append({
                    'username': username,
                    'password': password,
                    'result': result
                })

        if successful:
            self._log(f"Found {len(successful)} working credential(s)")
        else:
            self._log(f"No working credentials found")

        return successful

    def validate_credentials(self, url: str, username: str, password: str) -> Dict:
        """
        Validate if provided credentials work for the camera

        Args:
            url: RTSP URL to test
            username: Username to validate
            password: Password to validate

        Returns:
            Dictionary with validation results including:
            - valid: Boolean if credentials work
            - status_code: HTTP status code
            - error: Error message if any
            - codec: Video codec if accessible
            - resolution: Video resolution if accessible
        """
        self._log(f"Validating credentials for {url} with username: {username}")

        result = self.test_rtsp_with_auth(url, username, password)

        validation = {
            'url': url,
            'username': username,
            'valid': False,
            'status_code': result.get('status_code'),
            'error': result.get('error'),
            'response_time': result.get('response_time'),
            'codec': result.get('codec'),
            'resolution': result.get('resolution')
        }

        # Credentials are valid if we get 200 OK
        if result.get('reachable') and result.get('status_code') == 200:
            validation['valid'] = True
            self._log(f"✓ Credentials validated successfully for {url}")
        elif result.get('status_code') == 401:
            validation['error'] = "Invalid credentials (401 Unauthorized)"
            self._log(f"✗ Invalid credentials for {url}")
        else:
            self._log(f"✗ Could not validate credentials: {validation['error']}")

        return validation

    def verify_stream_playback(self, url: str, username: str = None, password: str = None) -> Dict:
        """
        Verify that the stream can actually play by sending SETUP and PLAY requests

        Args:
            url: RTSP URL to test
            username: Optional username
            password: Optional password

        Returns:
            Dictionary with playback verification results including:
            - playable: Boolean if stream can be played
            - setup_ok: Boolean if SETUP succeeded
            - play_ok: Boolean if PLAY succeeded
            - data_received: Boolean if actual video data was received
            - error: Error message if any
        """
        self._log(f"Verifying stream playback for {url}")

        result = {
            'url': url,
            'playable': False,
            'setup_ok': False,
            'play_ok': False,
            'data_received': False,
            'error': None
        }

        # First, test basic connection
        if username and password:
            test_result = self.test_rtsp_with_auth(url, username, password)
        else:
            test_result = self.test_rtsp_connection(url)

        if not test_result.get('reachable'):
            result['error'] = test_result.get('error', 'Not reachable')
            return result

        if test_result.get('status_code') not in [200, 401]:
            result['error'] = f"Invalid status code: {test_result.get('status_code')}"
            return result

        # If auth required but no credentials provided
        if test_result.get('status_code') == 401 and not (username and password):
            result['error'] = "Authentication required but no credentials provided"
            return result

        parsed = self.parse_rtsp_url(url)
        if not parsed:
            result['error'] = "Invalid URL"
            return result

        host = parsed['hostname']
        port = parsed['port']

        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((host, port))

            # Send SETUP request
            setup_request = (
                f"SETUP {url} RTSP/1.0\r\n"
                f"CSeq: 2\r\n"
                f"Transport: RTP/AVP;unicast;client_port=8000-8001\r\n"
                f"\r\n"
            )
            sock.sendall(setup_request.encode())
            setup_response = sock.recv(4096).decode('utf-8', errors='ignore')

            # Check SETUP response
            if 'RTSP/1.0 200 OK' in setup_response or 'Session:' in setup_response:
                result['setup_ok'] = True
                self._log(f"SETUP request successful", "debug")

                # Extract session ID
                session_match = re.search(r'Session:\s*([^\s;]+)', setup_response)
                session_id = session_match.group(1) if session_match else '12345678'

                # Send PLAY request
                play_request = (
                    f"PLAY {url} RTSP/1.0\r\n"
                    f"CSeq: 3\r\n"
                    f"Session: {session_id}\r\n"
                    f"\r\n"
                )
                sock.sendall(play_request.encode())
                play_response = sock.recv(4096).decode('utf-8', errors='ignore')

                # Check PLAY response
                if 'RTSP/1.0 200 OK' in play_response:
                    result['play_ok'] = True
                    self._log(f"PLAY request successful", "debug")

                    # Try to receive some data (this would be RTP packets in reality)
                    sock.settimeout(2.0)
                    try:
                        data = sock.recv(1024)
                        if len(data) > 0:
                            result['data_received'] = True
                            self._log(f"Received {len(data)} bytes of stream data", "debug")
                    except socket.timeout:
                        # Timeout is OK - it means PLAY worked but data comes via RTP
                        self._log(f"No immediate data (normal for RTP streams)", "debug")

                    # Stream is playable if PLAY succeeded
                    result['playable'] = True
                    self._log(f"✓ Stream is playable: {url}")
                else:
                    result['error'] = "PLAY request failed"
                    self._log(f"✗ PLAY request failed", "debug")
            else:
                result['error'] = "SETUP request failed"
                self._log(f"✗ SETUP request failed", "debug")

        except socket.timeout:
            result['error'] = "Connection timeout during playback test"
        except socket.error as e:
            result['error'] = f"Socket error: {str(e)}"
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass

        return result

    def generate_rtsp_url(self, host: str, port: int = 554, path: str = "/",
                         username: str = None, password: str = None) -> str:
        """
        Generate RTSP URL from components

        Args:
            host: Hostname or IP
            port: Port number (default: 554)
            path: URL path (default: "/")
            username: Optional username
            password: Optional password

        Returns:
            Complete RTSP URL
        """
        if username and password:
            return f"rtsp://{username}:{password}@{host}:{port}{path}"
        elif username:
            return f"rtsp://{username}@{host}:{port}{path}"
        else:
            return f"rtsp://{host}:{port}{path}"
