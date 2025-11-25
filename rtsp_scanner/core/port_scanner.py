"""Port scanner for RTSP services"""

import socket
import concurrent.futures
from typing import List, Dict, Tuple
from ipaddress import ip_network, IPv4Address
import time


class PortScanner:
    """Scanner for detecting RTSP services on network"""

    # Common RTSP ports
    DEFAULT_PORTS = [554, 8554, 7447, 5554, 88, 8000, 8080, 8888]

    def __init__(self, timeout: float = 2.0, max_workers: int = 50, logger=None):
        """
        Initialize port scanner

        Args:
            timeout: Connection timeout in seconds
            max_workers: Maximum number of concurrent workers
            logger: Logger instance
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.logger = logger
        self.results = []

    def _log(self, message: str, level: str = "info"):
        """Helper to log messages"""
        if self.logger:
            getattr(self.logger, level)(message)

    def scan_port(self, host: str, port: int) -> Tuple[str, int, bool, float]:
        """
        Scan a single port on a host

        Args:
            host: Target host IP
            port: Target port number

        Returns:
            Tuple of (host, port, is_open, response_time)
        """
        start_time = time.time()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                result = sock.connect_ex((host, port))
                response_time = time.time() - start_time

                if result == 0:
                    self._log(f"Port {port} is OPEN on {host} (response: {response_time:.3f}s)", "debug")
                    return (host, port, True, response_time)
                else:
                    self._log(f"Port {port} is CLOSED on {host}", "debug")
                    return (host, port, False, response_time)
        except socket.timeout:
            response_time = time.time() - start_time
            self._log(f"Timeout scanning {host}:{port}", "debug")
            return (host, port, False, response_time)
        except socket.error as e:
            response_time = time.time() - start_time
            self._log(f"Error scanning {host}:{port} - {str(e)}", "debug")
            return (host, port, False, response_time)
        except Exception as e:
            response_time = time.time() - start_time
            self._log(f"Unexpected error scanning {host}:{port} - {str(e)}", "error")
            return (host, port, False, response_time)

    def scan_host(self, host: str, ports: List[int] = None) -> List[Dict]:
        """
        Scan multiple ports on a single host

        Args:
            host: Target host IP
            ports: List of ports to scan (default: DEFAULT_PORTS)

        Returns:
            List of dictionaries containing scan results
        """
        if ports is None:
            ports = self.DEFAULT_PORTS

        self._log(f"Scanning host {host} on ports {ports}")

        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.scan_port, host, port) for port in ports]

            for future in concurrent.futures.as_completed(futures):
                host, port, is_open, response_time = future.result()
                if is_open:
                    result = {
                        'host': host,
                        'port': port,
                        'status': 'open',
                        'response_time': response_time
                    }
                    results.append(result)
                    self._log(f"Found open port: {host}:{port}")

        return results

    def scan_network(self, network: str, ports: List[int] = None) -> List[Dict]:
        """
        Scan a network range for RTSP services

        Args:
            network: Network in CIDR notation (e.g., "192.168.1.0/24")
            ports: List of ports to scan (default: DEFAULT_PORTS)

        Returns:
            List of dictionaries containing scan results
        """
        if ports is None:
            ports = self.DEFAULT_PORTS

        self._log(f"Scanning network {network} for RTSP services on ports {ports}")

        try:
            net = ip_network(network, strict=False)
            hosts = [str(ip) for ip in net.hosts()]

            self._log(f"Scanning {len(hosts)} hosts")

            all_results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Create tasks for each host-port combination
                futures = []
                for host in hosts:
                    for port in ports:
                        futures.append(executor.submit(self.scan_port, host, port))

                # Process results as they complete
                completed = 0
                total = len(futures)
                for future in concurrent.futures.as_completed(futures):
                    completed += 1
                    if completed % 100 == 0:
                        self._log(f"Progress: {completed}/{total} scans completed")

                    host, port, is_open, response_time = future.result()
                    if is_open:
                        result = {
                            'host': host,
                            'port': port,
                            'status': 'open',
                            'response_time': response_time
                        }
                        all_results.append(result)
                        self._log(f"Found open RTSP port: {host}:{port}")

            self._log(f"Scan complete. Found {len(all_results)} open ports")
            self.results = all_results
            return all_results

        except ValueError as e:
            self._log(f"Invalid network format: {network} - {str(e)}", "error")
            return []
        except Exception as e:
            self._log(f"Error scanning network: {str(e)}", "error")
            return []

    def scan_ip_range(self, start_ip: str, end_ip: str, ports: List[int] = None) -> List[Dict]:
        """
        Scan an IP range for RTSP services

        Args:
            start_ip: Starting IP address
            end_ip: Ending IP address
            ports: List of ports to scan

        Returns:
            List of dictionaries containing scan results
        """
        if ports is None:
            ports = self.DEFAULT_PORTS

        try:
            start = int(IPv4Address(start_ip))
            end = int(IPv4Address(end_ip))

            if start > end:
                self._log("Start IP must be less than or equal to end IP", "error")
                return []

            hosts = [str(IPv4Address(ip)) for ip in range(start, end + 1)]
            self._log(f"Scanning IP range {start_ip} to {end_ip} ({len(hosts)} hosts)")

            all_results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                for host in hosts:
                    for port in ports:
                        futures.append(executor.submit(self.scan_port, host, port))

                completed = 0
                total = len(futures)
                for future in concurrent.futures.as_completed(futures):
                    completed += 1
                    if completed % 100 == 0:
                        self._log(f"Progress: {completed}/{total} scans completed")

                    host, port, is_open, response_time = future.result()
                    if is_open:
                        result = {
                            'host': host,
                            'port': port,
                            'status': 'open',
                            'response_time': response_time
                        }
                        all_results.append(result)
                        self._log(f"Found open RTSP port: {host}:{port}")

            self._log(f"Scan complete. Found {len(all_results)} open ports")
            self.results = all_results
            return all_results

        except Exception as e:
            self._log(f"Error scanning IP range: {str(e)}", "error")
            return []

    def get_results(self) -> List[Dict]:
        """
        Get scan results

        Returns:
            List of scan results
        """
        return self.results
