// Level page: missing-line editor, in-browser runner (Pyodide), and the tutor flow.
(function () {
  "use strict";
  const { Progress, AISettings, api, escapeHtml, formatAiText } = window.Tutor;
  const cfg = window.LEVEL_CONFIG; // set in level.html
  const N = cfg.number;
  const RUN_TIMEOUT_MS = 5000;

  const $ = (id) => document.getElementById(id);
  const inputs = Array.from(document.querySelectorAll(".blank-input"));
  const runBtn = $("run-btn"), submitBtn = $("submit-btn"), hintBtn = $("hint-btn");
  const stdinBox = $("stdin"), outputBox = $("output"), feed = $("tutor-feed");

  // ------------------------------------------------------------ lock check
  if (!Progress.isUnlocked(N, cfg.levelNumbers)) {
    $("locked-overlay").hidden = false;
    return;
  }

  // ------------------------------------------------------------ restore state
  let state = Progress.level(N);
  if (!state.status) state = Progress.update(N, { status: "in_progress" });
  inputs.forEach((el, i) => { el.value = state.answers[i] || ""; });
  state.hintLog.forEach((h) => addMessage("hint", `Hint ${h.n}`, h.text, h.source));
  if (state.revealed) showReveal(state.revealed, false);

  function save(patch) {
    state = Progress.update(N, patch);
    renderStats();
  }

  function renderStats() {
    const left = cfg.maxHints - state.hints;
    $("stat-wrong").textContent = state.wrong;
    $("stat-hints").textContent = `${state.hints} / ${cfg.maxHints}`;
    hintBtn.textContent = `💡 Hint (${left} left)`;
    const finished = state.status === "passed" || state.status === "failed_revealed";
    hintBtn.disabled = finished || left <= 0;
    submitBtn.disabled = finished;
    inputs.forEach((el) => { el.readOnly = finished; });
    $("level-done").hidden = !finished;
    $("level-done").dataset.status = state.status;
    $("level-done-text").textContent = state.status === "passed"
      ? "🎉 Level passed!" : "Level finished (solution was shown - marked incorrect).";
  }
  renderStats();

  // ------------------------------------------------------------ editor helpers
  const answers = () => inputs.map((el) => el.value);

  function assemble() {
    let k = 0;
    return cfg.rows.map((r) => (r.blank ? r.indent + (inputs[k++].value || "").trim() : r.text)).join("\n") + "\n";
  }

  function markErrorLine(line) {
    document.querySelectorAll(".code-row.error").forEach((el) => el.classList.remove("error"));
    if (line) {
      const row = document.querySelector(`.code-row[data-line="${line}"]`);
      if (row) row.classList.add("error");
    }
  }

  inputs.forEach((el, i) => {
    el.addEventListener("input", () => { save({ answers: answers() }); markErrorLine(null); });
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); runCode(); }
      else if (e.key === "Enter") { e.preventDefault(); (inputs[i + 1] || submitBtn).focus(); }
    });
  });

  // ------------------------------------------------------------ tutor feed
  function addMessage(type, title, html, source) {
    const div = document.createElement("div");
    div.className = `msg msg-${type}`;
    const badge = source ? `<span class="src src-${source}">${source === "ai" ? "AI tutor" : "built-in"}</span>` : "";
    div.innerHTML = `<div class="msg-title">${escapeHtml(title)} ${badge}</div><div class="msg-body">${
      type === "hint" || type === "explain" ? formatAiText(html) : html}</div>`;
    feed.prepend(div);
    return div;
  }

  function busy(btn, on, label) {
    btn.disabled = on;
    if (label) btn.dataset.label = btn.dataset.label || btn.textContent;
    btn.textContent = on ? label : btn.dataset.label || btn.textContent;
    if (!on) renderStats();
  }

  // ------------------------------------------------------------ Pyodide runner
  let worker = null, workerReady = false, pending = null, runId = 0;

  function startWorker() {
    workerReady = false;
    $("py-status").textContent = "Loading Python… (first time can take ~10 s)";
    runBtn.disabled = true;
    worker = new Worker(`${cfg.workerUrl}?harness=${encodeURIComponent(cfg.harnessUrl)}`);
    worker.onmessage = (e) => {
      const m = e.data;
      if (m.type === "ready") {
        workerReady = true;
        runBtn.disabled = false;
        $("py-status").textContent = "Python ready ✓";
      } else if (m.type === "load_error") {
        $("py-status").textContent = "Could not load Python in the browser (internet needed). You can still Submit.";
      } else if (m.type === "result" && pending && m.id === pending.id) {
        clearTimeout(pending.timer);
        pending.resolve(m);
        pending = null;
      }
    };
  }
  startWorker();

  function runInWorker(code, stdin) {
    return new Promise((resolve) => {
      const id = ++runId;
      const timer = setTimeout(() => {
        pending = null;
        worker.terminate(); // stop an infinite loop
        startWorker();
        resolve({ output: "", error: "Your program took too long (more than 5 seconds). Is there a loop that never ends?" });
      }, RUN_TIMEOUT_MS);
      pending = { id, resolve, timer };
      worker.postMessage({ id, code, stdin });
    });
  }

  async function runCode() {
    if (!workerReady) return;
    busy(runBtn, true, "Running…");
    outputBox.textContent = "";
    outputBox.classList.remove("has-error");
    const res = await runInWorker(assemble(), stdinBox.value);
    let text = res.output || "";
    if (res.error) {
      const line = res.error_line ? `Line ${res.error_line}: ` : "";
      text += (text && !text.endsWith("\n") ? "\n" : "") + `❌ ${line}${res.error}`;
      outputBox.classList.add("has-error");
    }
    outputBox.textContent = text || "(no output)";
    markErrorLine(res.error_line);
    busy(runBtn, false);
  }
  runBtn.addEventListener("click", runCode);

  // ------------------------------------------------------------ Submit
  submitBtn.addEventListener("click", async () => {
    busy(submitBtn, true, "Checking…");
    try {
      const res = await api(`/api/check/${N}/`, { answers: answers(), wrong: state.wrong, hints: state.hints });
      markErrorLine(res.details && res.details.error_line);
      if (res.correct) {
        save({ status: "passed" });
        addMessage("success", "Correct!", escapeHtml(res.message));
        return;
      }
      if (res.counted) save({ wrong: state.wrong + 1 });

      let html = escapeHtml(res.message);
      const d = res.details || {};
      if (d.stdin) html += `<div class="io"><b>Test input:</b><pre>${escapeHtml(d.stdin)}</pre></div>`;
      if (res.kind === "output") {
        html += `<div class="io-grid"><div><b>Your output</b><pre>${escapeHtml(d.output || "(nothing)")}</pre></div>`
          + `<div><b>Expected output</b><pre>${escapeHtml(d.expected)}</pre></div></div>`;
      }
      if (res.action === "suggest_hint") {
        html += `<div class="nudge">Stuck? Press <b>💡 Hint</b> for help (${cfg.maxHints - state.hints} left).</div>`;
      }
      addMessage(res.counted ? "error" : "info", res.counted ? "Not quite" : "Almost ready", html);

      if (res.action === "reveal") await doReveal();
    } catch (err) {
      addMessage("error", "Error", escapeHtml(err.message));
    } finally {
      busy(submitBtn, false);
    }
  });

  // ------------------------------------------------------------ Hint
  hintBtn.addEventListener("click", async () => {
    if (state.hints >= cfg.maxHints) return;
    busy(hintBtn, true, "💡 Thinking…");
    try {
      const res = await api(`/api/hint/${N}/`, { answers: answers(), hints: state.hints, ai: AISettings.load() });
      if (!res.consumed) {
        addMessage("info", "Hint", escapeHtml(res.hint));
        return;
      }
      save({ hints: state.hints + 1, hintLog: [...state.hintLog, { n: res.hint_number, text: res.hint, source: res.source }] });
      const msg = addMessage("hint", `Hint ${res.hint_number}`, res.hint, res.source);
      if (res.ai_error) {
        msg.insertAdjacentHTML("beforeend", `<div class="ai-note">AI unavailable: ${escapeHtml(res.ai_error)}</div>`);
      }
    } catch (err) {
      addMessage("error", "Error", escapeHtml(err.message));
    } finally {
      busy(hintBtn, false);
    }
  });

  // ------------------------------------------------------------ Solution review
  async function doReveal() {
    const loading = addMessage("info", "Solution review", "All hints were used. Preparing an explanation…");
    try {
      const res = await api(`/api/reveal/${N}/`, { answers: answers(), hints: state.hints, ai: AISettings.load() });
      loading.remove();
      const revealed = { explanation: res.explanation, source: res.source, solution_lines: res.solution_lines, ai_error: res.ai_error };
      save({ status: "failed_revealed", revealed });
      showReveal(revealed, true);
    } catch (err) {
      loading.remove();
      addMessage("error", "Error", escapeHtml(err.message));
    }
  }

  function showReveal(revealed, fresh) {
    inputs.forEach((el, i) => {
      el.dataset.studentAnswer = el.value;
      el.value = revealed.solution_lines[i] || "";
      el.classList.add("revealed");
    });
    const sol = revealed.solution_lines.map((s, i) => `<div><b>Missing line ${i + 1}:</b> <code>${escapeHtml(s)}</code></div>`).join("");
    const msg = addMessage("explain", "Solution review (marked incorrect)", revealed.explanation, revealed.source);
    msg.insertAdjacentHTML("beforeend", `<div class="solution">${sol}<p class="muted">The correct lines are now in the editor - press ▶ Run to see them work.</p></div>`);
    if (fresh && revealed.ai_error) {
      msg.insertAdjacentHTML("beforeend", `<div class="ai-note">AI unavailable: ${escapeHtml(revealed.ai_error)}</div>`);
    }
  }
})();
