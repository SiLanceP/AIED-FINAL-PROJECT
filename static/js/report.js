// Report page: grade and 12-point score computed by the server from browser progress.
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
    $("total-points").textContent = `${res.total_points ?? 0} / ${res.max_points ?? 12}`;
    $("total-hints").textContent = `${res.total_hints} / ${res.max_total_hints ?? 36}`;
    $("total-wrong").textContent = res.total_wrong;

    $("level-rows").innerHTML = res.levels.map((r) => {
      const status = r.status === "locked" && Progress.isUnlocked(r.level, window.LEVEL_NUMBERS) ? "available" : r.status;
      return `<tr><td>Level ${r.level}</td><td>${escapeHtml(window.LEVEL_TITLES[r.level] || "")}</td>
        <td><span class="badge" data-status="${status}">${STATUS_LABELS[status] || status}</span></td>
        <td><b>${r.points ?? 0} / ${r.max_points ?? 4}</b></td>
        <td>${r.hints} / ${r.max_hints ?? 12}</td><td>${r.wrong}</td></tr>`;
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
