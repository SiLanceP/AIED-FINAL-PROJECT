from django.urls import path

from . import views

urlpatterns = [
    path("check/<int:number>/", views.check, name="api_check"),
    path("hint/<int:number>/", views.hint, name="api_hint"),
    path("reveal/<int:number>/", views.reveal, name="api_reveal"),
    path("grade/", views.grade, name="api_grade"),
]
