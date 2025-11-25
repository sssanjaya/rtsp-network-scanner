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

    def _log(self, message: str, level: str = "info"):
        """Helper to log messages"""
        if self.logger:
            getattr(self.logger, level)(message)

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

    def test_rtsp_connection(self, url: str) -> Dict:
        """
        Test RTSP connection by sending DESCRIBE request

        Args:
            url: RTSP URL to test

        Returns:
            Dictionary with test results
        """
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
        path = parsed['path']

        start_time = time.time()

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
                f"User-Agent: RTSP-Scanner/1.0\r\n"
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
                    result['reachable'] = True
                    result['response_time'] = response_time

                    # Extract server info
                    for line in lines:
                        if line.lower().startswith('server:'):
                            result['server_info'] = line.split(':', 1)[1].strip()
                            break

                    if status_code == 200:
                        self._log(f"RTSP connection successful: {url}")
                    elif status_code == 401:
                        self._log(f"RTSP requires authentication: {url}")
                        result['error'] = "Authentication required"
                    elif status_code == 404:
                        self._log(f"RTSP path not found: {url}")
                        result['error'] = "Path not found"
                    else:
                        result['error'] = f"Status code: {status_code}"
                else:
                    result['error'] = "Invalid RTSP response"

            sock.close()

        except socket.timeout:
            result['error'] = "Connection timeout"
            result['response_time'] = time.time() - start_time
            self._log(f"Connection timeout for {url}", "warning")
        except socket.error as e:
            result['error'] = f"Socket error: {str(e)}"
            result['response_time'] = time.time() - start_time
            self._log(f"Socket error for {url}: {str(e)}", "error")
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
            result['response_time'] = time.time() - start_time
            self._log(f"Error testing {url}: {str(e)}", "error")

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
