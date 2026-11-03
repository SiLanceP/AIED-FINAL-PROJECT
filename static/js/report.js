// Report page: grade is computed by the server from the browser's progress.
(function () {
  "use strict";
  const { Progress, AISettings, api, escapeHtml, formatAiText, STATUS_LABELS } = window.Tutor;
  const $ = (id) => document.getElementById(id);

  async function load(summarize) {
    const progress = Progress.load();
    const res = await api("/api/grade/", { levels: progress.levels, summarize, ai: AISettings.load() });

    $("grade").textContent = res.grade || "–";
    $("grade").dataset.grade = res.grade || "none";
    $("grade-reason").textContent = res.reason;
    $("total-hints").textContent = res.total_hints;
    $("total-wrong").textContent = res.total_wrong;

    $("level-rows").innerHTML = res.levels.map((r) => {
      const status = r.status === "locked" && Progress.isUnlocked(r.level, window.LEVEL_NUMBERS) ? "available" : r.status;
      return `<tr><td>Level ${r.level}</td><td>${escapeHtml(window.LEVEL_TITLES[r.level] || "")}</td>
        <td><span class="badge" data-status="${status}">${STATUS_LABELS[status] || status}</span></td>
        <td>${r.hints} / 3</td><td>${r.wrong}</td></tr>`;
    }).join("");

    if (res.complete) {
      $("summary-box").hidden = false;
      if (res.summary) {
        $("summary").innerHTML = formatAiText(res.summary);
        $("summary-src").textContent = res.summary_source === "ai" ? "AI tutor" : "built-in";
        $("summary-src").className = `src src-${res.summary_source}`;
      }
    }
    return res;
  }

  load(false).then((res) => {
    if (res.complete) {
      $("summary").textContent = "The AI tutor is writing your feedback…";
      load(true).catch((err) => { $("summary").textContent = err.message; });
    }
  }).catch((err) => { $("grade-reason").textContent = err.message; });
})();
