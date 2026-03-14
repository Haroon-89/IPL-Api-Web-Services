import os
import sys
import subprocess
import time
import signal
import urllib.request

def signal_handler(sig, frame):
    print("\nShutting down...")
    if 'api_proc' in globals():
        api_proc.terminate()
    if 'web_proc' in globals():
        web_proc.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def wait_for_api(url, timeout=120):
    print("Waiting for API to be ready", end="", flush=True)
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(url, timeout=2)
            print(" ✓")
            return True
        except:
            print(".", end="", flush=True)
            time.sleep(3)
    print(" ✗ Timed out")
    return False

def run_service(script_dir, name):
    if not os.path.exists(script_dir):
        print(f"Error: {name} directory '{script_dir}' not found.")
        return None

    script_path = os.path.join(script_dir, 'app.py')
    if not os.path.exists(script_path):
        print(f"Error: app.py not found in {script_dir}")
        return None

    proc = subprocess.Popen(
        [sys.executable, script_path],
        cwd=script_dir,
        env=os.environ.copy()
    )
    print(f"{name} started (PID: {proc.pid})")
    return proc

if __name__ == '__main__':
    print("Starting IPL Stats App...")

    api_dir = os.path.abspath('api')
    web_dir = os.path.abspath('web')

    api_proc = run_service(api_dir, "API")
    if not api_proc:
        sys.exit(1)

    if not wait_for_api("http://127.0.0.1:5000"):
        print("API failed to start — check your api/app.py")
        api_proc.terminate()
        sys.exit(1)

    web_proc = run_service(web_dir, "Web App")
    if not web_proc:
        api_proc.terminate()
        sys.exit(1)

    print("\n---")
    print("API  : http://127.0.0.1:5000")
    print("Web  : http://127.0.0.1:8000")
    print("Press Ctrl+C to stop.")
    print("---\n")

    try:
        web_proc.wait()
    except KeyboardInterrupt:
        pass
    finally:
        if api_proc:
            api_proc.terminate()
        if web_proc:
            web_proc.terminate()

    print("Both services stopped.")