import subprocess
import sys
import os
import time

def main():
    print("🚀 Starting Readora AI (Backend + Frontend)...")

    # Get the absolute paths for your directories
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")

    # 1. Start the FastAPI Backend
    # Using sys.executable guarantees it uses your activated virtual environment
    backend_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--reload"]
    print("-> Launching FastAPI Backend on port 8000...")
    backend_process = subprocess.Popen(backend_cmd, cwd=backend_dir)

    # Give the backend 3 seconds to fully boot up
    time.sleep(3)

    # 2. Start the Streamlit Frontend
    frontend_cmd = [sys.executable, "-m", "streamlit", "run", "FrontEnd/abc.py"]
    print("-> Launching Streamlit Frontend...")
    frontend_process = subprocess.Popen(frontend_cmd, cwd=root_dir)

    try:
        # Keep the script running to monitor both processes
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        # This catches when you press Ctrl+C and gracefully kills both servers
        print("\n🛑 Shutting down Readora AI processes...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()