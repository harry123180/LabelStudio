# -*- coding: utf-8 -*-
"""
Network Utilities
"""
import socket


def get_local_ip() -> str:
    """Get local network IP address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to external address to determine local IP
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip
