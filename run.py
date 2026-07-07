import os
import sys
import subprocess

def start_server():
    print("=" * 60)
    print("GhostNet -- The Ghost That Browses Before You")
    print("=" * 60)
    
    # Path to virtual environment python/uvicorn
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    
    if sys.platform == "win32":
        python_exe = os.path.join(backend_dir, "venv", "Scripts", "python.exe")
        uvicorn_exe = os.path.join(backend_dir, "venv", "Scripts", "uvicorn.exe")
    else:
        python_exe = os.path.join(backend_dir, "venv", "bin", "python")
        uvicorn_exe = os.path.join(backend_dir, "venv", "bin", "uvicorn")

    if not os.path.exists(python_exe):
        print(f"Error: Virtual environment not found at {os.path.join(backend_dir, 'venv')}")
        print("Please check your setup or re-run setup commands.")
        sys.exit(1)
        
    print("\nStarting GhostNet FastAPI backend...")
    print("Open your browser and navigate to: http://127.0.0.1:8000")
    print("Press Ctrl+C to terminate the server.\n")
    print("-" * 60)
    
    # Command to run uvicorn
    try:
        subprocess.run([uvicorn_exe, "main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"], cwd=backend_dir)
    except KeyboardInterrupt:
        print("\nGhostNet server stopped. Safe browsing!")
    except Exception as e:
        print(f"Error starting uvicorn: {e}")

if __name__ == "__main__":
    start_server()
