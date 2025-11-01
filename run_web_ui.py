"""
Script để chạy Streamlit Web UI.

Usage:
    python run_web_ui.py

Hoặc:
    streamlit run verimodel/web_ui.py
"""

import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "verimodel/web_ui.py",
        "--server.port=8501",
        "--server.address=0.0.0.0"
    ])

