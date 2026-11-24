// Level page: 4 exercises per level, missing-line editor, Pyodide runner, and tutor flow.
(function () {
  "use strict";
  const { Progress, AISettings, api, escapeHtml, formatAiText } = window.Tutor;
  const cfg = window.LEVEL_CONFIG; // set in level.html
  const N = cfg.number;
  const EXERCISES = cfg.exercises; // [{number, title, instructions_html, rows, sample_stdin}, ...]
  const EX_COUNT = EXERCISES.length;
  const RUN_TIMEOUT_MS = 5000;
  const FINISHED = ["passed", "failed_revealed"];

  const $ = (id) => document.getElementById(id);
  const runBtn = $("run-btn"), submitBtn = $("submit-btn"), hintBtn = $("hint-btn");
  const outputBox = $("output"), feed = $("tutor-feed");
  const editorBody = $("editor-body"), instructionsEl = $("instructions");
  const exDone = $("ex-done"), exDoneText = $("ex-done-text");
  const nextExBtn = $("next-ex-btn"), nextLevelBtn = $("next-level-btn");
  const tabBtns = Array.from(document.querySelectorAll(".ex-tab"));

  // ------------------------------------------------------------ lock check
  if (!Progress.isUnlocked(N, cfg.levelNumbers)) {
    $("locked-overlay").hidden = false;
    return;
  }

  let levelState = Progress.level(N);
  if (!levelState.status) levelState = Progress.update(N, { status: "in_progress" });

  let currentExNum = levelState.currentEx || 1;
  // Default to the first unfinished exercise if currentEx is invalid
  if (!EXERCISES.some((e) => e.number === currentExNum)) currentExNum = 1;
  let inputs = [];

  function getExDef(exNum) {
    return EXERCISES.find((e) => e.number === exNum) || EXERCISES[0];
  }

  function isExUnlocked(exNum) {
    if (Progress.isUnlockAll() || exNum <= 1) return true;
    const prev = Progress.exercise(N, exNum - 1);
    return FINISHED.includes(prev.status);
  }

  function recomputeLevelStatus() {
    levelState = Progress.level(N);
    const statuses = EXERCISES.map((e) => Progress.exercise(N, e.number).status);
    if (statuses.every((s) => FINISHED.includes(s))) {
      const anyRevealed = statuses.some((s) => s === "failed_revealed");
      const finalStatus = anyRevealed ? "failed_revealed" : "passed";
      if (levelState.status !== finalStatus) {
        levelState = Progress.update(N, { status: finalStatus });
      }
    } else if (FINISHED.includes(levelState.status)) {
      levelState = Progress.update(N, { status: "in_progress" });
    }
  }

  function renderTabs() {
    tabBtns.forEach((btn) => {
      const num = Number(btn.dataset.ex);
      const exState = Progress.exercise(N, num);
      const unlocked = isExUnlocked(num);
      btn.classList.toggle("active", num === currentExNum);
      btn.disabled = !unlocked;
      btn.dataset.status = exState.status || (unlocked ? "available" : "locked");
      const stateEl = btn.querySelector(".ex-tab-state");
      if (exState.status === "passed") stateEl.textContent = "✓ 1/1 pt";
      else if (exState.status === "failed_revealed") stateEl.textContent = "0/1 pt";
      else if (!unlocked) stateEl.textContent = "🔒";
      else stateEl.textContent = "1 pt";
    });
  }

  function renderStats() {
    levelState = Progress.level(N);
    const exState = Progress.exercise(N, currentExNum);
    const left = Math.max(0, cfg.maxHints - exState.hints);
    const pts = Progress.levelPoints(N, EX_COUNT);

    $("stat-points").textContent = `${pts} / ${EX_COUNT}`;
    $("stat-wrong").textContent = levelState.wrong;
    $("stat-hints").textContent = `${exState.hints} / ${cfg.maxHints}`;
    hintBtn.textContent = `💡 Hint (${left} left)`;

    const exFinished = FINISHED.includes(exState.status);
    hintBtn.disabled = exFinished || left <= 0;
    submitBtn.disabled = exFinished;
    inputs.forEach((el) => { el.readOnly = exFinished; });

    exDone.hidden = !exFinished;
    exDone.dataset.status = exState.status || "";
    const allFinished = EXERCISES.every((e) => FINISHED.includes(Progress.exercise(N, e.number).status));
    if (exFinished) {
      if (exState.status === "passed") {
        exDoneText.textContent = allFinished
          ? `🎉 Exercise ${currentExNum} passed (+1 pt)! You finished Level ${N}!`
          : `🎉 Exercise ${currentExNum} passed (+1 pt)!`;
      } else {
        exDoneText.textContent = `Exercise ${currentExNum} finished (solution shown — 0 pts).`;
      }
      const hasNextEx = currentExNum < EX_COUNT;
      nextExBtn.hidden = !hasNextEx;
      nextLevelBtn.hidden = hasNextEx || !allFinished;
      if (exState.status === "passed" && allFinished) {
        exDoneText.textContent = `🎉 Exercise ${currentExNum} passed (+1 pt)! You finished Level ${N}!`;
      }
    } else {
      nextExBtn.hidden = true;
      nextLevelBtn.hidden = true;
    }
    renderTabs();
  }

  function buildEditor(exDef, exState) {
    editorBody.innerHTML = exDef.rows.map((r) => {
      if (r.blank) {
        return `<div class="code-row blank" data-line="${r.n}">
          <span class="ln">${r.n}</span>
          <span class="indent">${escapeHtml(r.indent)}</span>
          <input class="blank-input" type="text" data-index="${r.blank_index}"
                 placeholder="Type missing line ${r.blank_index + 1} here…"
                 spellcheck="false" autocomplete="off" autocapitalize="off" autocorrect="off">
        </div>`;
      }
      return `<div class="code-row" data-line="${r.n}">
        <span class="ln">${r.n}</span>
        <code class="language-python static-line">${r.text ? escapeHtml(r.text) : " "}</code>
      </div>`;
    }).join("");

    editorBody.querySelectorAll(".static-line").forEach((el) => window.hljs && hljs.highlightElement(el));
    inputs = Array.from(editorBody.querySelectorAll(".blank-input"));
    inputs.forEach((el, i) => {
      el.value = (exState.answers && exState.answers[i]) || "";
      el.addEventListener("input", () => {
        Progress.updateExercise(N, currentExNum, { answers: answers() });
        markErrorLine(null);
      });
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); runCode(); }
        else if (e.key === "Enter") { e.preventDefault(); (inputs[i + 1] || submitBtn).focus(); }
      });
    });
  }

  function selectExercise(exNum) {
    if (!isExUnlocked(exNum)) return;
    activeRunSession++;
    if (workerReady) {
      runBtn.disabled = false;
      runBtn.textContent = runBtn.dataset.label || "▶ Run";
    }
    currentExNum = exNum;
    Progress.update(N, { currentEx: exNum });
    const exDef = getExDef(exNum);
    const exState = Progress.exercise(N, exNum);

    $("ex-title").textContent = `✏️ Exercise ${exDef.number} of ${EX_COUNT}: ${exDef.title}`;
    instructionsEl.innerHTML = exDef.instructions_html;
    outputBox.textContent = "Press ▶ Run to try your code.";
    outputBox.classList.remove("has-error");

    buildEditor(exDef, exState);

    feed.innerHTML = `<div class="msg msg-info"><div class="msg-body">Fill in the missing lines for <b>Exercise ${exDef.number}</b>, press <b>▶ Run</b> to test, then <b>✓ Submit</b>.</div></div>`;
    (exState.hintLog || []).forEach((h) => addMessage("hint", `Hint ${h.n}`, h.text, h.source));
    if (exState.passNote) {
      addMessage("success", `Exercise ${exDef.number} Correct! (+1 pt)`, exState.passNote.text, exState.passNote.source);
    }
    if (exState.revealed) showReveal(exState.revealed, false);

    recomputeLevelStatus();
    renderStats();
  }

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => selectExercise(Number(btn.dataset.ex)));
  });

  nextExBtn.addEventListener("click", () => {
    if (currentExNum < EX_COUNT) selectExercise(currentExNum + 1);
  });

  // ------------------------------------------------------------ editor helpers
  const answers = () => inputs.map((el) => el.value);

  function assemble() {
    const exDef = getExDef(currentExNum);
    let k = 0;
    return exDef.rows.map((r) => (r.blank ? r.indent + (inputs[k++].value || "").trim() : r.text)).join("\n") + "\n";
  }

  function markErrorLine(line) {
    editorBody.querySelectorAll(".code-row.error").forEach((el) => el.classList.remove("error"));
    if (line) {
      const row = editorBody.querySelector(`.code-row[data-line="${line}"]`);
      if (row) row.classList.add("error");
    }
  }

  // ------------------------------------------------------------ tutor feed
  function addMessage(type, title, html, source) {
    const div = document.createElement("div");
    div.className = `msg msg-${type}`;
    const badge = source ? `<span class="src src-${source}">${source === "ai" ? "AI tutor" : "built-in"}</span>` : "";
    div.innerHTML = `<div class="msg-title">${escapeHtml(title)} ${badge}</div><div class="msg-body">${
      type === "hint" || type === "explain" || type === "success" ? formatAiText(html) : html}</div>`;
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
    const sep = cfg.workerUrl.includes("?") ? "&" : "?";
    worker = new Worker(`${cfg.workerUrl}${sep}harness=${encodeURIComponent(cfg.harnessUrl)}`);
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

  function runInWorker(code, stdin, interactive) {
    return new Promise((resolve) => {
      const id = ++runId;
      const timer = setTimeout(() => {
        pending = null;
        worker.terminate();
        startWorker();
        resolve({ output: "", error: "Your program took too long (more than 5 seconds). Is there a loop that never ends?", need_input: false, prompt: "" });
      }, RUN_TIMEOUT_MS);
      pending = { id, resolve, timer };
      worker.postMessage({ id, code, stdin, interactive: Boolean(interactive) });
    });
  }

  let activeRunSession = 0;

  function askTerminalInput(outputSoFar, promptText, sessionId) {
    return new Promise((resolve) => {
      outputBox.innerHTML = "";
      if (outputSoFar) {
        const pre = document.createElement("span");
        pre.textContent = outputSoFar;
        outputBox.appendChild(pre);
      }
      const line = document.createElement("div");
      line.className = "term-input-line";
      const promptSpan = document.createElement("span");
      promptSpan.className = "term-prompt";
      promptSpan.textContent = promptText || "> ";
      const field = document.createElement("input");
      field.type = "text";
      field.className = "term-input";
      field.placeholder = "Type input and press Enter…";
      field.autocomplete = "off";
      field.spellcheck = false;
      line.appendChild(promptSpan);
      line.appendChild(field);
      outputBox.appendChild(line);
      outputBox.scrollTop = outputBox.scrollHeight;
      field.focus();

      field.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          if (sessionId !== activeRunSession) return;
          const val = field.value;
          field.disabled = true;
          resolve(val);
        }
      });
    });
  }

  async function runCode() {
    if (!workerReady) return;
    const sessionId = ++activeRunSession;
    const code = assemble();
    busy(runBtn, true, "Running…");
    outputBox.textContent = "";
    outputBox.classList.remove("has-error");

    if (cfg.interactiveTerminal) {
      const collected = [];
      let res;
      while (true) {
        const stdin = collected.join("\n");
        res = await runInWorker(code, stdin, true);
        if (sessionId !== activeRunSession) return;
        if (!res.need_input) break;
        const typed = await askTerminalInput(res.output || "", res.prompt || "", sessionId);
        if (sessionId !== activeRunSession) return;
        collected.push(typed);
      }
      let text = res.output || "";
      if (res.error) {
        const line = res.error_line ? `Line ${res.error_line}: ` : "";
        text += (text && !text.endsWith("\n") ? "\n" : "") + `❌ ${line}${res.error}`;
        outputBox.classList.add("has-error");
      }
      outputBox.textContent = text || "(no output)";
      markErrorLine(res.error_line);
      busy(runBtn, false);
      return;
    }

    const sampleStdin = getExDef(currentExNum).sample_stdin || "";
    const res = await runInWorker(code, sampleStdin, false);
    if (sessionId !== activeRunSession) return;
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
      levelState = Progress.level(N);
      const exState = Progress.exercise(N, currentExNum);
      const res = await api(`/api/check/${N}/`, {
        exercise: currentExNum,
        answers: answers(),
        wrong: exState.wrong,
        hints: exState.hints,
      });
      markErrorLine(res.details && res.details.error_line);
      if (res.correct) {
        const submittedAnswers = answers();
        const exNum = currentExNum;
        const instantText = res.explanation || res.message;
        Progress.updateExercise(N, exNum, {
          status: "passed",
          answers: submittedAnswers,
          passNote: { text: instantText, source: "builtin" },
        });
        recomputeLevelStatus();
        const msgEl = addMessage("success", `Exercise ${exNum} Correct! (+1 pt)`, instantText, "builtin");
        // Try to upgrade to a personalized AI explanation in the background without blocking navigation
        api(`/api/explain/${N}/`, {
          exercise: exNum,
          answers: submittedAnswers,
          ai: AISettings.load(),
        }).then((exp) => {
          if (exp && exp.explanation && exp.source === "ai") {
            Progress.updateExercise(N, exNum, { passNote: { text: exp.explanation, source: "ai" } });
            if (currentExNum === exNum && msgEl.isConnected) {
              const titleEl = msgEl.querySelector(".msg-title");
              const bodyEl = msgEl.querySelector(".msg-body");
              if (titleEl) titleEl.innerHTML = `${escapeHtml(`Exercise ${exNum} Correct! (+1 pt)`)} <span class="src src-ai">AI tutor</span>`;
              if (bodyEl) bodyEl.innerHTML = formatAiText(exp.explanation);
            }
          }
        }).catch(() => { /* keep the instant built-in explanation */ });
        return;
      }
      if (res.counted) {
        Progress.updateExercise(
          N,
          currentExNum,
          { wrong: exState.wrong + 1, answers: answers() },
          { wrong: levelState.wrong + 1 }
        );
      }

      let html = escapeHtml(res.message);
      const d = res.details || {};
      if (d.stdin) html += `<div class="io"><b>Test input:</b><pre>${escapeHtml(d.stdin)}</pre></div>`;
      if (res.kind === "output") {
        html += `<div class="io-grid"><div><b>Your output</b><pre>${escapeHtml(d.output || "(nothing)")}</pre></div>`
          + `<div><b>Expected output</b><pre>${escapeHtml(d.expected)}</pre></div></div>`;
      }
      const updatedEx = Progress.exercise(N, currentExNum);
      if (res.action === "suggest_hint" && updatedEx.hints < cfg.maxHints) {
        html += `<div class="nudge">Stuck? Press <b>💡 Hint</b> for help (${cfg.maxHints - updatedEx.hints} left for this exercise).</div>`;
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
    const exState = Progress.exercise(N, currentExNum);
    if (exState.hints >= cfg.maxHints) return;
    busy(hintBtn, true, "💡 Thinking…");
    try {
      const res = await api(`/api/hint/${N}/`, {
        exercise: currentExNum,
        answers: answers(),
        hints: exState.hints,
        ai: AISettings.load(),
      });
      if (!res.consumed) {
        addMessage("info", "Hint", escapeHtml(res.hint));
        return;
      }
      const nextHintLog = [...(exState.hintLog || []), { n: res.hint_number, text: res.hint, source: res.source }];
      const nextExHints = exState.hints + 1;
      Progress.updateExercise(
        N,
        currentExNum,
        { hints: nextExHints, hintLog: nextHintLog, answers: answers() }
      );
      Progress.update(N, { hints: Progress.levelHints(N, EX_COUNT) });
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
      const exState = Progress.exercise(N, currentExNum);
      const res = await api(`/api/reveal/${N}/`, {
        exercise: currentExNum,
        answers: answers(),
        hints: exState.hints,
        ai: AISettings.load(),
      });
      loading.remove();
      const revealed = {
        explanation: res.explanation,
        source: res.source,
        solution_lines: res.solution_lines,
        ai_error: res.ai_error,
      };
      Progress.updateExercise(N, currentExNum, { status: "failed_revealed", revealed });
      recomputeLevelStatus();
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
    const msg = addMessage("explain", "Solution review (marked incorrect — 0 pts)", revealed.explanation, revealed.source);
    msg.insertAdjacentHTML("beforeend", `<div class="solution">${sol}<p class="muted">The correct lines are now in the editor - press ▶ Run to see them work.</p></div>`);
    if (fresh && revealed.ai_error) {
      msg.insertAdjacentHTML("beforeend", `<div class="ai-note">AI unavailable: ${escapeHtml(revealed.ai_error)}</div>`);
    }
  }

  // Initialize first unfinished or saved exercise
  const firstUnfinished = EXERCISES.find((e) => !FINISHED.includes(Progress.exercise(N, e.number).status));
  if (!isExUnlocked(currentExNum)) {
    currentExNum = firstUnfinished ? firstUnfinished.number : 1;
  }
  selectExercise(currentExNum);
})();
