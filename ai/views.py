import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .providers import AIUnavailable, default_provider, public_presets, test_connection


def settings_page(request):
    return render(
        request,
        "settings.html",
        {"presets": public_presets(), "default_provider": default_provider()},
    )


@require_POST
def test_ai(request):
    try:
        data = json.loads(request.body or "{}")
        return JsonResponse(test_connection(data.get("ai") or {}))
    except AIUnavailable as e:
        return JsonResponse({"ok": False, "message": str(e), "models": []})
    except (ValueError, TypeError):
        return JsonResponse({"ok": False, "message": "Bad request."}, status=400)
