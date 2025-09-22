#!/usr/bin/env python3
"""
Diagnostic script to check system and port availability
"""

import socket
import sys
import os

def check_port(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            return True
    except OSError as e:
        print(f"Port {port}: {e}")
        return False

def main():
    print("=== System Diagnostic ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in directory: {os.listdir('.')}")
    print()
    
    print("=== Port Availability Check ===")
    ports_to_check = [8000, 8001, 8002, 8080, 8081, 8082]
    
    available_ports = []
    for port in ports_to_check:
        if check_port(port):
            print(f"Port {port}: ✅ Available")
            available_ports.append(port)
        else:
            print(f"Port {port}: ❌ Not available")
    
    print()
    if available_ports:
        print(f"✅ Available ports: {available_ports}")
        print(f"Recommended port: {available_ports[0]}")
    else:
        print("❌ No ports available in the tested range")
        print("This might indicate a system-level issue")
    
    print()
    print("=== Network Interface Check ===")
    try:
        # Try to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"Local IP: {local_ip}")
    except Exception as e:
        print(f"Could not determine local IP: {e}")

if __name__ == "__main__":
    main()
