r"""Run the PyTutor AI server in TEST MODE with all levels and exercises unlocked.

Usage:
    .\.venv\Scripts\python run_test_unlocked.py

Open http://127.0.0.1:8000 in your browser — every level (1–3) and every
exercise (1–4 in each level) will be unlocked so you can jump straight to any
exercise without completing previous ones first.

Stop the server (Ctrl+C) and run normal `python manage.py runserver` to go back
to standard sequential locking.
"""

import os
import socket
import sys


def _port_in_use(host, port):
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def _parse_addr(addr):
    if ":" in addr:
        host, port_str = addr.rsplit(":", 1)
        return host or "127.0.0.1", int(port_str)
    if addr.isdigit():
        return "127.0.0.1", int(addr)
    return addr, 8000


def main():
    os.environ["UNLOCK_ALL"] = "1"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aitutor.settings")

    from django.core.management import execute_from_command_line

    args = sys.argv[1:] or ["127.0.0.1:8000"]
    if os.environ.get("RUN_MAIN") != "true":
        host, port = _parse_addr(args[0])
        if _port_in_use(host, port):
            print(
                f"\nERROR: Another server (such as `manage.py runserver`) is already running on {host}:{port}.\n"
                "Close your old server terminals (or run `taskkill /F /IM python.exe` in PowerShell),\n"
                "then run `python run_test_unlocked.py` again — or use another port:\n"
                "    python run_test_unlocked.py 127.0.0.1:8001\n"
            )
            sys.exit(1)
        print("\n" + "=" * 64)
        print("  TEST MODE: All levels (1-3) and exercises (1-4) are UNLOCKED")
        print(f"  Open http://{args[0]} in your browser")
        print("  Press Ctrl+C to stop.")
        print("=" * 64 + "\n")
    execute_from_command_line(["manage.py", "runserver", *args])


if __name__ == "__main__":
    main()
