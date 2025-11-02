"""
Vercel Serverless Entry Point for VeriModel API

This file serves as the entry point for Vercel deployment.
It imports and mounts the FastAPI app from verimodel.api_server.
"""

import sys
from pathlib import Path

# Add parent directory to path to import verimodel
sys.path.insert(0, str(Path(__file__).parent.parent))

from verimodel.api_server import app

# Export the app for Vercel
# Vercel will automatically detect this as a WSGI/ASGI app
__all__ = ["app"]

