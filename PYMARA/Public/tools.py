from django.http import JsonResponse
import json


def error(code, msg):
    try:
        JsonResponse({'code': code, 'error': msg})
    except Exception as e:
        print(e)
        print('---转换失败,上面是报错信息,请联系高---')
        return JsonResponse({'code': code, 'error':'转JSON的时候出错了' })


def good(msg=''):
    if not msg:
        return JsonResponse({'code':200})
    try:
        return JsonResponse({'code': 200, 'data': msg})
    except Exception as e:
        print(e)
        print('---转换失败,上面是报错信息,请联系高---')
        return JsonResponse({'code': 200, 'data': '转JSON的时候出错了'})
