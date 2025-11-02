"""
Script để chạy FastAPI server.

Usage:
    python run_api.py

Hoặc:
    uvicorn verimodel.api_server:app --host 0.0.0.0 --port 8000 --reload
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting VeriModel Server...")
    print("📡 Server will be available at:")
    print("   - http://localhost:8000")
    print("   - http://127.0.0.1:8000")
    print("\n⚠️  Note: Use 'localhost' or '127.0.0.1' in your browser, NOT '0.0.0.0'\n")
    
    uvicorn.run(
        "verimodel.api_server:app",
        host="0.0.0.0",  # Listen on all interfaces
        port=8000,
        reload=True
    )

