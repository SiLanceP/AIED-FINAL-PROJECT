from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("level/<int:number>/", views.level_detail, name="level"),
    path("report/", views.report, name="report"),
]
