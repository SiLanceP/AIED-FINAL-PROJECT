// Shared browser helpers: progress in localStorage, AI settings, API calls.
(function () {
  "use strict";

  const PROGRESS_KEY = "aied_progress_v1";
  const AI_KEY = "aied_ai_settings_v1"; // kept separate so "Reset Progress" keeps AI settings
  const FINISHED = ["passed", "failed_revealed"];

  // ---------------------------------------------------------------- progress
  const Progress = {
    load() {
      try {
        const data = JSON.parse(localStorage.getItem(PROGRESS_KEY));
        if (data && data.levels) return data;
      } catch (_) { /* corrupted -> start fresh */ }
      return { version: 1, levels: {} };
    },
    save(data) {
      localStorage.setItem(PROGRESS_KEY, JSON.stringify(data));
    },
    level(n) {
      const lv = this.load().levels[String(n)] || {};
      return { status: null, wrong: 0, hints: 0, answers: [], hintLog: [], ...lv };
    },
    update(n, patch) {
      const data = this.load();
      data.levels[String(n)] = { ...this.level(n), ...patch };
      this.save(data);
      return data.levels[String(n)];
    },
    isFinished(n) {
      return FINISHED.includes(this.level(n).status);
    },
    isUnlocked(n, numbers) {
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
        pill.textContent = p === "none" ? "AI: off" : `AI: ${preset.label.split(" (")[0]} · ${s.model || preset.model}`;
        pill.dataset.kind = preset.kind;
      }
    }
  });

  window.Tutor = { Progress, AISettings, api, escapeHtml, formatAiText, STATUS_LABELS };
})();
