from django.urls import path
from . import views

urlpatterns = [
    # http://127.0.0.1:8000/v1/logreg/judge_phone_number
    path("judge_phone_number", views.JudgePhoneNumber.as_view()),

    # http://127.0.0.1:8000/v1/logreg/register
    path("register", views.Register.as_view()),

    # http://127.0.0.1:8000/v1/logreg/send_message
    path("send_message", views.SendMessage.as_view()),

    # http://127.0.0.1:8000/v1/logreg/login
    path("login", views.UserLogin.as_view()),
]


