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
import sys


def main():
    os.environ["UNLOCK_ALL"] = "1"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aitutor.settings")

    from django.core.management import execute_from_command_line

    args = sys.argv[1:] or ["127.0.0.1:8000"]
    if os.environ.get("RUN_MAIN") != "true":
        print("\n" + "=" * 64)
        print("  TEST MODE: All levels (1-3) and exercises (1-4) are UNLOCKED")
        print(f"  Open http://{args[0]} in your browser")
        print("  Press Ctrl+C to stop.")
        print("=" * 64 + "\n")
    execute_from_command_line(["manage.py", "runserver", *args])


if __name__ == "__main__":
    main()
