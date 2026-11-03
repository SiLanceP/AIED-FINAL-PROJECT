from .providers import default_provider, public_presets


def ai_presets(request):
    return {"ai_presets": public_presets(), "ai_default_provider": default_provider()}
