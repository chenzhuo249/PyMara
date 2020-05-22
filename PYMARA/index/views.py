from django.views import View
from django.http import JsonResponse
from Public.publictoken import logging_check

class JudgeLogin(View):

    @logging_check
    def post(self, request):
        user = request.my_user

        return JsonResponse({"code":200, "data": user.username})
