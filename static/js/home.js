// Home page: level cards with status from localStorage.
(function () {
  "use strict";
  const { Progress, STATUS_LABELS } = window.Tutor;
  const numbers = window.LEVEL_NUMBERS;

  let finished = 0;
  numbers.forEach((n) => {
    const card = document.querySelector(`.level-card[data-level="${n}"]`);
    const status = Progress.displayStatus(n, numbers);
    const lv = Progress.level(n);
    card.dataset.status = status;
    card.querySelector(".badge").textContent = STATUS_LABELS[status];
    card.querySelector(".card-stats").textContent =
      status === "locked" || status === "available" ? "" : `Hints: ${lv.hints}/3 · Incorrect: ${lv.wrong}`;
    const btn = card.querySelector(".card-btn");
    if (status === "locked") {
      btn.textContent = "🔒 Locked";
      btn.classList.add("disabled");
      btn.removeAttribute("href");
    } else {
      btn.textContent = { available: "Start", in_progress: "Continue" }[status] || "Review";
    }
    if (Progress.isFinished(n)) finished++;
  });

  const pct = Math.round((finished / numbers.length) * 100);
  document.getElementById("progress-fill").style.width = `${pct}%`;
  document.getElementById("progress-text").textContent = `${finished} of ${numbers.length} levels finished`;
  if (finished === numbers.length) document.getElementById("report-cta").hidden = false;
})();
