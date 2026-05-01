"""
Financial App Launcher
======================
Launches the Financial App (FastAPI backend + React frontend) with a single click.

Usage:
    python app_launcher.py          # Run directly with Python
    financial_app.exe               # Run as compiled executable

Controls:
    Ctrl+C  - Gracefully stop both backend and frontend
"""

import os
import sys
import time
import shutil
import signal
import socket
import subprocess
import threading
import webbrowser

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BACKEND_PORT = 8000
FRONTEND_PORT = 5173
BROWSER_URL = f"http://localhost:{FRONTEND_PORT}"
STARTUP_WAIT_SECONDS = 5   # seconds to wait for each service to become available

# Determine the project root (works both for .py and PyInstaller .exe)
if getattr(sys, "frozen", False):
    # Running as a PyInstaller bundle
    PROJECT_ROOT = os.path.dirname(sys.executable)
else:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_banner():
    print("=" * 60)
    print("  💰 Financial App Launcher")
    print("=" * 60)
    print()


def log(message: str):
    """Print a timestamped log line."""
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {message}")


def is_port_in_use(port: int) -> bool:
    """Return True if the given TCP port is already bound."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) == 0


def check_dependency(cmd: str) -> bool:
    """Return True if *cmd* is available on PATH."""
    return shutil.which(cmd) is not None


def check_dependencies() -> bool:
    """Verify that Python, Node.js, and npm are installed."""
    log("Checking required dependencies…")
    ok = True
    for dep in ("python", "node", "npm"):
        if check_dependency(dep):
            log(f"  ✅ {dep} found")
        else:
            log(f"  ❌ {dep} NOT found — please install it before running this app")
            ok = False
    print()
    return ok


def stream_output(process: subprocess.Popen, prefix: str):
    """Read stdout/stderr from *process* and print each line with *prefix*."""
    try:
        for line in iter(process.stdout.readline, b""):
            decoded = line.decode("utf-8", errors="replace").rstrip()
            if decoded:
                print(f"[{prefix}] {decoded}")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Service management
# ---------------------------------------------------------------------------

processes: list[subprocess.Popen] = []


def start_backend() -> subprocess.Popen:
    """Start the FastAPI backend with uvicorn."""
    if is_port_in_use(BACKEND_PORT):
        log(f"⚠️  Port {BACKEND_PORT} is already in use — skipping backend start.")
        log(f"   If a stale process is running, stop it and try again.")
        return None

    log(f"🚀 Starting Backend  (http://localhost:{BACKEND_PORT}) …")

    # Use the same Python interpreter that is running this script so that the
    # correct virtualenv / packages are picked up.
    python_exe = sys.executable if not getattr(sys, "frozen", False) else "python"

    proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "main:app", "--reload",
         "--port", str(BACKEND_PORT)],
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    processes.append(proc)

    # Stream backend logs in a background thread
    t = threading.Thread(target=stream_output, args=(proc, "BACKEND"), daemon=True)
    t.start()

    return proc


def start_frontend() -> subprocess.Popen:
    """Start the React / Vite dev server."""
    if is_port_in_use(FRONTEND_PORT):
        log(f"⚠️  Port {FRONTEND_PORT} is already in use — skipping frontend start.")
        log(f"   If a stale process is running, stop it and try again.")
        return None

    log(f"🎨 Starting Frontend (http://localhost:{FRONTEND_PORT}) …")

    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"

    proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    processes.append(proc)

    # Stream frontend logs in a background thread
    t = threading.Thread(target=stream_output, args=(proc, "FRONTEND"), daemon=True)
    t.start()

    return proc


def wait_for_port(port: int, timeout: int = 60) -> bool:
    """Block until the port is accepting connections or *timeout* seconds pass."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_port_in_use(port):
            return True
        time.sleep(0.5)
    return False


def shutdown(signum=None, frame=None):
    """Terminate all child processes and exit cleanly."""
    print()
    log("🛑 Shutting down — stopping all services…")
    for proc in processes:
        try:
            proc.terminate()
        except Exception:
            pass
    # Give processes a moment to clean up
    time.sleep(1)
    for proc in processes:
        try:
            proc.kill()
        except Exception:
            pass
    log("👋 Goodbye!")
    sys.exit(0)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    print_banner()

    # Graceful shutdown on Ctrl+C (SIGINT) or SIGTERM
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # 1. Dependency check
    if not check_dependencies():
        log("❌ One or more dependencies are missing. Exiting.")
        sys.exit(1)

    # 2. Validate project directories
    for label, path in [("Backend", BACKEND_DIR), ("Frontend", FRONTEND_DIR)]:
        if not os.path.isdir(path):
            log(f"❌ {label} directory not found: {path}")
            log("   Make sure you are running the launcher from the project root.")
            sys.exit(1)

    # 3. Start services
    backend_proc = start_backend()
    frontend_proc = start_frontend()

    if backend_proc is None and frontend_proc is None:
        log("Both services appear to already be running.")
    else:
        # 4. Wait for services to become available
        log(f"⏳ Waiting for services to be ready (up to {STARTUP_WAIT_SECONDS}s)…")
        print()

        if backend_proc is not None:
            if wait_for_port(BACKEND_PORT, timeout=STARTUP_WAIT_SECONDS):
                log(f"✅ Backend  ready at http://localhost:{BACKEND_PORT}")
            else:
                log(f"⚠️  Backend did not start within {STARTUP_WAIT_SECONDS}s — check logs above")

        if frontend_proc is not None:
            if wait_for_port(FRONTEND_PORT, timeout=STARTUP_WAIT_SECONDS):
                log(f"✅ Frontend ready at http://localhost:{FRONTEND_PORT}")
            else:
                log(f"⚠️  Frontend did not start within {STARTUP_WAIT_SECONDS}s — check logs above")

    # 5. Open browser
    print()
    log(f"🌐 Opening browser → {BROWSER_URL}")
    webbrowser.open(BROWSER_URL)

    # 6. Keep running and print status
    print()
    print("=" * 60)
    print("  ✅  Financial App is running!")
    print(f"     Backend  → http://localhost:{BACKEND_PORT}")
    print(f"     Frontend → http://localhost:{FRONTEND_PORT}")
    print()
    print("  Press Ctrl+C to stop all services and exit.")
    print("=" * 60)
    print()

    # Stay alive until the user interrupts
    try:
        while True:
            # Detect if a child process has died unexpectedly
            for proc in list(processes):
                if proc.poll() is not None:
                    log(f"⚠️  A service process exited unexpectedly (PID {proc.pid})")
                    processes.remove(proc)
            time.sleep(2)
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()
