// AI Settings page: choose a free online provider or a local LLM.
(function () {
  "use strict";
  const { AISettings, api, escapeHtml } = window.Tutor;
  const presets = window.AI_PRESETS;
  const $ = (id) => document.getElementById(id);
  const providerSel = $("provider"), modelIn = $("model"), keyIn = $("api_key"), urlIn = $("base_url");

  const saved = AISettings.load();
  providerSel.value = saved.provider || window.AI_DEFAULT_PROVIDER;
  modelIn.value = saved.model || "";
  keyIn.value = saved.api_key || "";
  urlIn.value = saved.base_url || "";

  function current() {
    const p = providerSel.value;
    const kind = presets[p].kind;
    return {
      provider: p,
      model: modelIn.value.trim(),
      api_key: kind === "cloud" ? keyIn.value.trim() : "",
      base_url: kind === "local" ? urlIn.value.trim() : "",
    };
  }

  function populateModels(models, activeModel) {
    const list = $("model-list");
    list.innerHTML = (models || []).map((m) => `<option value="${escapeHtml(m)}">`).join("");
    if (!modelIn.value && activeModel) {
      modelIn.value = activeModel;
    }
  }

  async function autoFetchLocalModels() {
    const p = presets[providerSel.value];
    if (p.kind !== "local") return;
    try {
      const qs = new URLSearchParams({ provider: providerSel.value, base_url: urlIn.value.trim() });
      const res = await fetch(`/api/ai/models/?${qs}`);
      if (!res.ok) return;
      const data = await res.json();
      populateModels(data.models, data.active_model);
    } catch (_) { /* ignore on initial load */ }
  }

  function render() {
    const p = presets[providerSel.value];
    document.querySelectorAll("[data-show]").forEach((el) => {
      el.hidden = !el.dataset.show.split(" ").includes(p.kind);
    });
    modelIn.placeholder = p.model ? `default: ${p.model}` : "";
    urlIn.placeholder = p.base_url ? `default: ${p.base_url}` : "";
    $("key-link").href = p.key_url;
    $("key-link").textContent = p.kind === "local" ? `Download ${p.label.split(" (")[0]}` : "Get a free API key";
    $("server-key-note").hidden = !p.server_has_key;
    autoFetchLocalModels();
  }

  providerSel.addEventListener("change", () => { modelIn.value = ""; render(); });
  render();

  $("save-btn").addEventListener("click", () => {
    AISettings.save(current());
    $("result").className = "result ok";
    $("result").textContent = "Saved ✓ These settings are stored only in this browser.";
  });

  $("test-btn").addEventListener("click", async () => {
    const btn = $("test-btn");
    btn.disabled = true;
    btn.textContent = "Testing…";
    $("result").className = "result";
    $("result").textContent = "Contacting the AI… (local models may take a while to load the first time)";
    try {
      const res = await api("/api/ai/test/", { ai: current() });
      $("result").className = `result ${res.ok ? "ok" : "bad"}`;
      $("result").textContent = res.message;
      populateModels(res.models, res.active_model);
      if (res.ok) {
        AISettings.save(current());
        $("result").textContent += " (Saved ✓)";
      }
    } catch (err) {
      $("result").className = "result bad";
      $("result").textContent = err.message;
    } finally {
      btn.disabled = false;
      btn.textContent = "Test connection";
    }
  });
})();
