"""Free AI providers behind one OpenAI-compatible interface.

Every provider below exposes an OpenAI-compatible ``/chat/completions`` endpoint,
so the free ``openai`` Python package works for all of them by changing
``base_url``. No paid service is required.

Settings come from two places (request wins over .env):
  * the browser (localStorage "AI Settings" page): provider, model, api_key, base_url
  * the server .env file: GEMINI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, ...
"""

import ipaddress
import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from openai import OpenAI, OpenAIError

PRESETS = {
    "gemini": {
        "label": "Google Gemini (online, free tier)",
        "kind": "cloud",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-2.5-flash",
        "env_key": "GEMINI_API_KEY",
        "key_url": "https://aistudio.google.com/apikey",
    },
    "groq": {
        "label": "Groq (online, free tier)",
        "kind": "cloud",
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.1-8b-instant",
        "env_key": "GROQ_API_KEY",
        "key_url": "https://console.groq.com/keys",
    },
    "openrouter": {
        "label": "OpenRouter (online, free ':free' models)",
        "kind": "cloud",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "env_key": "OPENROUTER_API_KEY",
        "key_url": "https://openrouter.ai/keys",
    },
    "ollama": {
        "label": "Ollama (local, on this computer)",
        "kind": "local",
        "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5-coder:7b",
        "env_key": "OLLAMA_BASE_URL",
        "key_url": "https://ollama.com/download",
    },
    "lmstudio": {
        "label": "LM Studio (local, on this computer)",
        "kind": "local",
        "base_url": "http://localhost:1234/v1",
        "model": "local-model",
        "env_key": "LMSTUDIO_BASE_URL",
        "key_url": "https://lmstudio.ai",
    },
    "none": {
        "label": "No AI (use built-in hints only)",
        "kind": "none",
        "base_url": "",
        "model": "",
        "env_key": "",
        "key_url": "",
    },
}


class AIUnavailable(Exception):
    """Raised when the AI cannot be used; callers fall back to static content."""


@dataclass
class AIConfig:
    provider: str
    model: str
    base_url: str
    api_key: str
    kind: str

    @property
    def timeout(self):
        # Local models can be slow, especially on the first request (model loading).
        return 120 if self.kind == "local" else 30


def _is_local_url(url):
    host = urlparse(url).hostname or ""
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback or ipaddress.ip_address(host).is_private
    except ValueError:
        return False


def default_provider():
    p = os.getenv("DEFAULT_AI_PROVIDER", "ollama")
    return p if p in PRESETS else "ollama"


def _normalize_base_url(url, kind):
    url = (url or "").strip().rstrip("/")
    if kind == "local" and url and not url.endswith("/v1"):
        url = url + "/v1"
    return url


def _list_models(cfg):
    try:
        return sorted(m.id for m in _client(cfg).models.list())[:100]
    except OpenAIError:
        return []


def resolve_config(user_settings=None):
    """Merge browser settings + .env + presets into an AIConfig."""
    s = user_settings or {}
    provider = s.get("provider") or default_provider()
    if provider not in PRESETS:
        raise AIUnavailable(f"Unknown AI provider '{provider}'.")
    preset = PRESETS[provider]
    if preset["kind"] == "none":
        return AIConfig(provider, "", "", "", "none")

    user_model = (s.get("model") or "").strip() or os.getenv(f"{provider.upper()}_MODEL")
    model = user_model or preset["model"]

    if preset["kind"] == "local":
        # Only local providers may change the URL, and only to a local/private address.
        raw_url = (s.get("base_url") or "").strip() or os.getenv(preset["env_key"]) or preset["base_url"]
        base_url = _normalize_base_url(raw_url, "local")
        if not _is_local_url(base_url):
            raise AIUnavailable("Local AI URL must point to localhost or a private network address.")
        api_key = provider  # Ollama / LM Studio ignore the key, but the client requires one.
    else:
        base_url = preset["base_url"]
        api_key = (s.get("api_key") or "").strip() or os.getenv(preset["env_key"], "")
        if not api_key:
            raise AIUnavailable(
                f"No API key for {preset['label']}. Add one in AI Settings or in the server .env file."
            )
    cfg = AIConfig(provider, model, base_url, api_key, preset["kind"])
    # For local providers: if the user left Model blank (or the default isn't installed),
    # automatically pick an installed model so it works out of the box.
    if cfg.kind == "local":
        installed = _list_models(cfg)
        if installed and cfg.model not in installed:
            if not user_model:
                # Prefer a larger instruct/coder model if available, otherwise first installed
                preferred = [m for m in installed if "7b" in m.lower() or "coder" in m.lower()]
                cfg.model = preferred[-1] if preferred else installed[0]
            else:
                raise AIUnavailable(
                    f"Model '{cfg.model}' is not installed in {preset['label']}. "
                    f"Installed models: {', '.join(installed)}"
                )
    return cfg


_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def _client(cfg):
    return OpenAI(base_url=cfg.base_url, api_key=cfg.api_key, timeout=cfg.timeout, max_retries=1)


def chat(user_settings, system_prompt, user_prompt, max_tokens=400):
    """Send one chat request. Returns (text, AIConfig). Raises AIUnavailable."""
    cfg = resolve_config(user_settings)
    if cfg.kind == "none":
        raise AIUnavailable("AI is turned off in AI Settings.")
    try:
        resp = _client(cfg).chat.completions.create(
            model=cfg.model,
            temperature=0.3,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except OpenAIError as e:
        raise AIUnavailable(f"{PRESETS[cfg.provider]['label']}: {type(e).__name__}: {str(e)[:200]}") from e
    text = (resp.choices[0].message.content or "") if resp.choices else ""
    text = _THINK_RE.sub("", text).strip()  # strip reasoning from "thinking" models (qwen3, deepseek-r1)
    if not text:
        raise AIUnavailable("The AI returned an empty response.")
    return text, cfg


def test_connection(user_settings):
    """Check settings by listing models (if supported) and sending a tiny prompt."""
    cfg = resolve_config(user_settings)
    if cfg.kind == "none":
        return {"ok": True, "message": "AI is turned off. Built-in hints will be used.", "models": [], "active_model": ""}
    models = _list_models(cfg)
    reply, cfg = chat(user_settings, "You are a test endpoint.", "Reply with exactly: OK", max_tokens=20)
    return {
        "ok": True,
        "message": f"Connected to {PRESETS[cfg.provider]['label']} using model '{cfg.model}'. Reply: {reply[:60]}",
        "models": models,
        "active_model": cfg.model,
    }


def public_presets():
    """Preset info that is safe to send to the browser (no keys)."""
    return {
        name: {
            "label": p["label"],
            "kind": p["kind"],
            "model": p["model"],
            "base_url": p["base_url"] if p["kind"] == "local" else "",
            "key_url": p["key_url"],
            "server_has_key": bool(p["kind"] == "cloud" and os.getenv(p["env_key"])),
        }
        for name, p in PRESETS.items()
    }
