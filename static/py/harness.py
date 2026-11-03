"""Shared code runner used by BOTH the browser (Pyodide) and the Django server.

- In the browser, ``py-worker.js`` loads this file into Pyodide and calls ``run_code``.
- On the server, ``tutor/runner.py`` launches this file as a subprocess and sends a
  JSON job on stdin; the result is printed as JSON on stdout.

Keeping a single file guarantees that "Run" in the browser and "Submit" on the
server behave the same way.
"""

import builtins
import io
import json
import sys
import traceback

MAX_OUTPUT_CHARS = 10_000
FILENAME = "main.py"


class _OutputLimit(Exception):
    pass


class _LimitedWriter(io.StringIO):
    def write(self, s):
        if self.tell() + len(s) > MAX_OUTPUT_CHARS:
            super().write(s[: max(0, MAX_OUTPUT_CHARS - self.tell())])
            raise _OutputLimit()
        return super().write(s)


def run_code(code, stdin_text="", echo=True):
    """Run ``code`` feeding ``stdin_text`` (one value per line) to ``input()``.

    echo=True  -> behave like a terminal: show input() prompts and typed values.
    echo=False -> only output produced by print() is captured (used for grading,
                  so the prompt text inside input() is never graded).

    Returns a dict: {"output": str, "error": str | None, "error_line": int | None}
    """
    out = _LimitedWriter()
    lines = stdin_text.splitlines()
    pos = [0]

    def _input(prompt=""):
        if echo:
            out.write(str(prompt))
        if pos[0] >= len(lines):
            raise EOFError(
                "The program asked for input, but there are no more values in the Input box."
            )
        value = lines[pos[0]]
        pos[0] += 1
        if echo:
            out.write(value + "\n")
        return value

    old_out, old_err, real_input = sys.stdout, sys.stderr, builtins.input
    sys.stdout = sys.stderr = out
    builtins.input = _input
    error, error_line = None, None
    try:
        exec(compile(code, FILENAME, "exec"), {"__name__": "__main__", "__builtins__": builtins})
    except _OutputLimit:
        error = "Output limit reached (your program printed too much - is there an endless loop?)."
    except SyntaxError as e:  # includes IndentationError
        error_line = e.lineno
        error = f"{type(e).__name__}: {e.msg}"
    except BaseException as e:  # noqa: BLE001 - we want to report everything to the student
        frames = [f for f in traceback.extract_tb(e.__traceback__) if f.filename == FILENAME]
        error_line = frames[-1].lineno if frames else None
        error = f"{type(e).__name__}: {e}"
    finally:
        sys.stdout, sys.stderr, builtins.input = old_out, old_err, real_input
    return {"output": out.getvalue(), "error": error, "error_line": error_line}


def _main():
    """Server entry point: JSON job on stdin -> JSON results on stdout."""
    job = json.loads(sys.stdin.read())
    real_stdout = sys.stdout
    results = [run_code(job["code"], case, job.get("echo", False)) for case in job["cases"]]
    real_stdout.write(json.dumps(results))


# In Pyodide (browser) __name__ is also "__main__", so skip the server entry point there.
if __name__ == "__main__" and sys.platform != "emscripten":
    _main()
