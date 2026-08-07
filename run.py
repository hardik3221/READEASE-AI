import subprocess
import sys
import os
import time

def main():
    print("🚀 Starting Readora AI (Backend + Frontend)...")

    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")

    # Pass backend_dir into PYTHONPATH so 'import app...' works globally
    env = os.environ.copy()
    env["PYTHONPATH"] = backend_dir + os.pathsep + env.get("PYTHONPATH", "")

    # 1. Start FastAPI Backend from the backend directory
    backend_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--reload"]
    print("-> Launching FastAPI Backend on port 8000...")
    backend_process = subprocess.Popen(backend_cmd, cwd=backend_dir, env=env)

    time.sleep(3)
    if backend_process.poll() is not None:
        print("\n❌ FastAPI Backend failed to start. See error above.")
        sys.exit(1)

    # 2. Start Streamlit Frontend
    frontend_cmd = [sys.executable, "-m", "streamlit", "run", "FrontEnd/app.py"]
    print("-> Launching Streamlit Frontend...")
    frontend_process = subprocess.Popen(frontend_cmd, cwd=root_dir, env=env)

    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Readora AI processes...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()