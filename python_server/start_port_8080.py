#!/usr/bin/env python3
"""
Startup script for the Unified Exam Proctoring System on port 8080
"""

import uvicorn

if __name__ == "__main__":
    print("Starting Unified Exam Proctoring System on port 8080...")
    print("Server will be available at: http://localhost:8080")
    print("API Docs: http://localhost:8080/docs")
    print("Press Ctrl+C to stop the server")
    print()
    
    uvicorn.run(
        "unified_exam_server:app",
        host="127.0.0.1",
        port=8080,
        reload=False
    )
