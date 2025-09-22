#!/usr/bin/env python3
"""
Startup script for the Unified Exam Proctoring System
"""

import uvicorn
import sys
import os
import socket

def is_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def find_available_port(start_port=8000, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    return None

def main():
    """Start the unified exam server"""
    print("Starting Unified Exam Proctoring System...")
    print("=" * 50)
    
    # Try to find an available port
    port = find_available_port(8000)
    if port is None:
        print("ERROR: No available ports found in range 8000-8009")
        print("Please close other applications or try again later")
        sys.exit(1)
    
    if port != 8000:
        print(f"Port 8000 is busy, using port {port} instead")
    
    print("Server will be available at:")
    print(f"  - API: http://localhost:{port}")
    print(f"  - Docs: http://localhost:{port}/docs")
    print(f"  - ReDoc: http://localhost:{port}/redoc")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        uvicorn.run(
            "unified_exam_server:app",
            host="127.0.0.1",  # Use localhost instead of 0.0.0.0 for Windows
            port=port,
            reload=False,  # Disable reload to avoid issues
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except OSError as e:
        if e.errno == 10013:  # Windows permission error
            print(f"\nERROR: Permission denied on port {port}")
            print("This is usually caused by:")
            print("1. Another application using the port")
            print("2. Windows Firewall blocking the port")
            print("3. Antivirus software blocking the connection")
            print("\nTry running as Administrator or use a different port")
        else:
            print(f"\nNetwork error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
