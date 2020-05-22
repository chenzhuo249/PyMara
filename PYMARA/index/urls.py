from django.urls import path
from . import views

urlpatterns = [

    # http://127.0.0.1:8000/v1/index/judge_login
    path("judge_login", views.JudgeLogin.as_view())
]