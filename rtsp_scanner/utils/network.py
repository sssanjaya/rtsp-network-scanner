"""Network utility functions"""

import socket
import platform


def get_local_network():
    """
    Auto-detect local network subnet

    Returns:
        str: Network in CIDR notation (e.g., "192.168.1.0/24")
    """
    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        # Convert to /24 subnet
        parts = local_ip.split('.')
        network = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"

        return network
    except Exception:
        # Fallback to common private network
        return "192.168.1.0/24"


def get_local_ip():
    """
    Get local IP address

    Returns:
        str: Local IP address
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"
