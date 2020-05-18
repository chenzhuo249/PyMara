from django.http import JsonResponse
import json


def error(code, msg=''):
    try:
        data = json.dumps(msg)
    except:
        data = str(msg)
    return JsonResponse({'code': code, 'error': data})


def good(msg=''):
    if not msg:
        return JsonResponse({'code':200})
    try:
        data = json.dumps(msg)
    except:
        data = str(msg)
    return JsonResponse({'code': 200, 'data': data})
