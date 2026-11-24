// Shared browser helpers: progress in localStorage, AI settings, API calls.
(function () {
  "use strict";

  const PROGRESS_KEY = "aied_progress_v1";
  const UNLOCK_ALL_KEY = "aied_unlock_all";
  // v2: Automatic mode became the default, so older saved choices are reset once.
  const AI_KEY = "aied_ai_settings_v2"; // kept separate so "Reset Progress" keeps AI settings
  const FINISHED = ["passed", "failed_revealed"];

  // ---------------------------------------------------------------- progress
  const Progress = {
    isUnlockAll() {
      return Boolean(window.UNLOCK_ALL) || localStorage.getItem(UNLOCK_ALL_KEY) === "1";
    },
    setUnlockAll(on) {
      if (on) localStorage.setItem(UNLOCK_ALL_KEY, "1");
      else localStorage.removeItem(UNLOCK_ALL_KEY);
    },
    load() {
      try {
        const data = JSON.parse(localStorage.getItem(PROGRESS_KEY));
        if (data && data.levels) return data;
      } catch (_) { /* corrupted -> start fresh */ }
      return { version: 2, levels: {} };
    },
    save(data) {
      localStorage.setItem(PROGRESS_KEY, JSON.stringify(data));
    },
    level(n) {
      const lv = this.load().levels[String(n)] || {};
      return { status: null, wrong: 0, hints: 0, currentEx: 1, exercises: {}, ...lv };
    },
    exercise(levelN, exN) {
      const lv = this.level(levelN);
      const ex = (lv.exercises && lv.exercises[String(exN)]) || {};
      return { status: null, wrong: 0, answers: [], hintLog: [], revealed: null, ...ex };
    },
    update(n, patch) {
      const data = this.load();
      data.levels[String(n)] = { ...this.level(n), ...patch };
      this.save(data);
      return data.levels[String(n)];
    },
    updateExercise(levelN, exN, exPatch, levelPatch) {
      const lv = this.level(levelN);
      const exercises = { ...(lv.exercises || {}) };
      exercises[String(exN)] = { ...this.exercise(levelN, exN), ...exPatch };
      return this.update(levelN, { ...(levelPatch || {}), exercises });
    },
    levelPoints(levelN, exCount) {
      const lv = this.level(levelN);
      const exMap = lv.exercises || {};
      let pts = 0;
      for (let i = 1; i <= (exCount || 4); i++) {
        if ((exMap[String(i)] || {}).status === "passed") pts++;
      }
      return pts;
    },
    isFinished(n) {
      return FINISHED.includes(this.level(n).status);
    },
    isUnlocked(n, numbers) {
      if (this.isUnlockAll()) return true;
      const idx = numbers.indexOf(n);
      return idx === 0 || (idx > 0 && this.isFinished(numbers[idx - 1]));
    },
    // locked | available | in_progress | passed | failed_revealed
    displayStatus(n, numbers) {
      const s = this.level(n).status;
      if (s) return s;
      return this.isUnlocked(n, numbers) ? "available" : "locked";
    },
    reset() {
      localStorage.removeItem(PROGRESS_KEY);
    },
  };

  // ---------------------------------------------------------------- AI settings
  const AISettings = {
    load() {
      try {
        return JSON.parse(localStorage.getItem(AI_KEY)) || {};
      } catch (_) {
        return {};
      }
    },
    save(s) {
      localStorage.setItem(AI_KEY, JSON.stringify(s));
    },
  };

  // ---------------------------------------------------------------- API
  function csrfToken() {
    const m = document.querySelector('meta[name="csrf-token"]');
    return m ? m.content : "";
  }

  async function api(url, body) {
    let res;
    try {
      res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
        body: JSON.stringify(body || {}),
      });
    } catch (err) {
      throw new Error(
        "Could not reach the Django server (" + err.message + "). Make sure the server is running and open http://127.0.0.1:8000."
      );
    }
    let data = {};
    try { data = await res.json(); } catch (_) { /* non-JSON error page */ }
    if (!res.ok) throw new Error(data.error || data.message || `Server error (${res.status})`);
    return data;
  }

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => (
      { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
    ));
  }

  // Tiny formatter for AI text: escapes HTML, supports `inline code`, **bold** and line breaks.
  function formatAiText(s) {
    return escapeHtml(s)
      .replace(/```(?:python)?\n?([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");
  }

  const STATUS_LABELS = {
    locked: "Locked",
    available: "Not started",
    in_progress: "In progress",
    passed: "Passed",
    failed_revealed: "Solution shown",
  };

  // ---------------------------------------------------------------- reset button + AI pill
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-reset-progress]").forEach((btn) =>
      btn.addEventListener("click", () => {
        if (confirm("Reset ALL your progress? Your levels, attempts and hints will be erased. This cannot be undone.")) {
          Progress.reset();
          window.location.href = "/";
        }
      })
    );
    const pill = document.getElementById("ai-pill");
    if (pill && window.AI_PRESETS) {
      const s = AISettings.load();
      const p = s.provider || window.AI_DEFAULT_PROVIDER;
      const preset = window.AI_PRESETS[p];
      if (preset) {
        if (p === "none") pill.textContent = "AI: off";
        else if (p === "auto") pill.textContent = "AI: Automatic";
        else pill.textContent = `AI: ${preset.label.split(" (")[0]} · ${s.model || preset.model}`;
        pill.dataset.kind = preset.kind === "auto" ? "cloud" : preset.kind;
      }
    }
  });

  window.Tutor = { Progress, AISettings, api, escapeHtml, formatAiText, STATUS_LABELS };
})();
