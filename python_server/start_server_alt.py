#!/usr/bin/env python3
"""
Alternative startup script for the Unified Exam Proctoring System
Uses port 8080 by default to avoid Windows permission issues
"""

import uvicorn
import sys
import os

def main():
    """Start the unified exam server on port 8080"""
    print("Starting Unified Exam Proctoring System...")
    print("=" * 50)
    print("Server will be available at:")
    print("  - API: http://localhost:8080")
    print("  - Docs: http://localhost:8080/docs")
    print("  - ReDoc: http://localhost:8080/redoc")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        uvicorn.run(
            "unified_exam_server:app",
            host="127.0.0.1",
            port=8080,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        print("\nIf you get permission errors, try:")
        print("1. Run PowerShell as Administrator")
        print("2. Use a different port (modify this script)")
        print("3. Check Windows Firewall settings")
        sys.exit(1)

if __name__ == "__main__":
    main()
