"""Runs student code on the server in a separate Python process.

Student code is NEVER executed inside the Django process. Each submission is run
by ``static/py/harness.py`` in an isolated (``-I``) subprocess with a timeout.
Combined with the AST safety checks in ``checker.py`` this is adequate for a
class project; it is not a hardened sandbox.
"""

import json
import subprocess
import sys

from django.conf import settings


class CodeTimeout(Exception):
    pass


def run_cases(code, cases, echo=False):
    """Run ``code`` once per stdin case. Returns a list of harness result dicts."""
    job = json.dumps({"code": code, "cases": list(cases) or [""], "echo": echo})
    try:
        proc = subprocess.run(
            [sys.executable, "-I", str(settings.HARNESS_PATH)],
            input=job,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=settings.CODE_RUN_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as e:
        raise CodeTimeout() from e
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        msg = (proc.stderr or "Unknown error while running code.").strip().splitlines()[-1:]
        return [{"output": "", "error": " ".join(msg), "error_line": None} for _ in (cases or [""])]
