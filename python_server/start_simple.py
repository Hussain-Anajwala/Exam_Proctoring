#!/usr/bin/env python3
"""
Simple startup script for the Unified Exam Proctoring System
"""

import uvicorn

if __name__ == "__main__":
    print("Starting Unified Exam Proctoring System...")
    print("Server will be available at: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print()
    
    uvicorn.run(
        "unified_exam_server:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )
