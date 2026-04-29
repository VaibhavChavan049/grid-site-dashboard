#!/usr/bin/env python3
"""
One-command launcher for Grid Site Dashboard.
Starts both FastAPI backend and Streamlit frontend.
"""

import subprocess
import sys
import os
import time
import threading

def run_backend():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "backend.api:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])

def run_frontend():
    time.sleep(3)  # Wait for backend to start
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "frontend/dashboard.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])

if __name__ == "__main__":
    print("=" * 55)
    print("  ⚡ Grid Site Intelligence Dashboard")
    print("  Starting backend + frontend...")
    print("=" * 55)

    # Generate data first
    print("\n[1/3] Generating grid site data...")
    subprocess.run([sys.executable, "data/generate_data.py"])

    print("\n[2/3] Starting FastAPI backend on http://localhost:8000")
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()

    print("[3/3] Starting Streamlit dashboard on http://localhost:8501")
    run_frontend()
