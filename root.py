import os
import sys
import subprocess
import time
import signal

def signal_handler(sig, frame):
    print("\nShutting down...")
    if 'api_proc' in globals():
        api_proc.terminate()
    if 'web_proc' in globals():
        web_proc.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C

def run_service(script_dir, port, name):
    """Run a Flask app in a subprocess with absolute paths."""
    if not os.path.exists(script_dir):
        print(f"Error: {name} directory '{script_dir}' not found. Ensure you're in the project root.")
        return None
    
    script_path = os.path.join(script_dir, 'app.py')
    if not os.path.exists(script_path):
        print(f"Error: app.py not found in {script_dir}")
        return None
    
    # Use subprocess with cwd set to dir
    cmd = [sys.executable, script_path]
    env = os.environ.copy()  # Inherit venv if activated
    
    proc = subprocess.Popen(
        cmd,
        cwd=script_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid if os.name != 'nt' else None  # For clean kill on Unix
    )
    print(f"{name} started (PID: {proc.pid})")
    return proc

if __name__ == '__main__':
    print("Starting IPL Stats App...")
    
    # Absolute paths to subdirs
    api_dir = os.path.abspath('api')
    web_dir = os.path.abspath('web')
    
    # Start API first
    api_proc = run_service(api_dir, 5000, "API")
    if not api_proc:
        sys.exit(1)
    
    time.sleep(3)  # Wait for API to boot (adjust if needed)
    
    # Start Web
    web_proc = run_service(web_dir, 8000, "Web App")
    if not web_proc:
        api_proc.terminate()
        sys.exit(1)
    
    print("\n---")
    print("API: http://localhost:5000")
    print("Web: http://localhost:8000")
    print("Press Ctrl+C to stop.")
    print("---\n")
    
    try:
        # Wait for web to finish (foreground)
        web_proc.wait()
    except KeyboardInterrupt:
        pass
    finally:
        if api_proc:
            api_proc.terminate()
        if web_proc:
            web_proc.terminate()
    
    print("Both services stopped.")