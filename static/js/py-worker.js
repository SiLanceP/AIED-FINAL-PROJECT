// Web Worker that runs Python in the browser with Pyodide (WebAssembly).
// Running in a worker keeps the page responsive; the page terminates the worker
// if a program runs too long (e.g. an infinite loop).
/* global importScripts, loadPyodide */
importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js");

const harnessUrl = new URLSearchParams(self.location.search).get("harness");

const ready = (async () => {
  const pyodide = await loadPyodide();
  const src = await (await fetch(harnessUrl)).text();
  pyodide.runPython(src); // defines run_code(code, stdin_text, echo)
  self.postMessage({ type: "ready" });
  return pyodide;
})().catch((err) => {
  self.postMessage({ type: "load_error", error: String(err) });
});

self.onmessage = async (event) => {
  const pyodide = await ready;
  if (!pyodide) return;
  const { id, code, stdin } = event.data;
  const runCode = pyodide.globals.get("run_code");
  try {
    const res = runCode(code, stdin || "", true);
    const obj = res.toJs({ dict_converter: Object.fromEntries });
    res.destroy();
    self.postMessage({ type: "result", id, ...obj });
  } catch (err) {
    self.postMessage({ type: "result", id, output: "", error: String(err), error_line: null });
  } finally {
    runCode.destroy();
  }
};
