from django.urls import path

from . import views

urlpatterns = [
    path("settings/", views.settings_page, name="ai_settings"),
    path("api/ai/test/", views.test_ai, name="ai_test"),
]
