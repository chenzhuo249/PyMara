"""
登录令牌
{'code': 403, 'error': '登录信息过期'}
{'code': 444, 'error': '账号权限被限制'}
"""

import copy
import json
import base64
import time
import hmac
from django.http import JsonResponse
from django.conf import settings
from user.models import User

def logging_check(fun):
    def wrapper(self, request, *args, **kwargs):
        print('---进入验证---')
        token = request.META.get('HTTP_PYMARATOKEN')
        if not token:
            return JsonResponse({'code': 403, 'error': '请登录!'})
        try:
            payload = Jwt().my_decode(token, settings.JWT_TOKEN_KEY)
        except:
            return JsonResponse({'code': 403, 'error': '登录信息过期'})
        id = payload['id'] # 登录用户的id
        phone = payload["phone"] # 登录用户的手机号(本项目的账号)

        # 如果body里有参数
        if request.body:
            json_obj = json.loads(request.body.decode())
            request.my_data = json_obj # 视图函数从这里取, json对象
        try:
            print(id)
            user = User.objects.get(id=id, status=0)
            print(user.username)
            request.my_user = user # 登录的用户对象, MyModel对象(User表实例)
        except:
            return JsonResponse({'code': 444, 'error': '账号权限被限制'})
        print('---通过验证---')
        return fun(self, request, *args, **kwargs)

    return wrapper


class Jwt:
    def __init__(self):
        pass

    @staticmethod
    def my_encode(my_payload, key, exp=3600 * 24):
        """
        制作token令牌
        :param my_payload:私有声明
        :param key: token_key
        :param exp: 有效时间
        :return: 字符串类型token
        """
        header = {'typ': 'JWT', 'alg': 'HS256'}
        # 转json
        header_json = json.dumps(header, separators=(',', ':'), sort_keys=True)
        # urlsafe_b64encode加密去空格
        header_bs = Jwt.b64encode(header_json.encode())
        # 深拷贝字典防止改变原字典
        payload = copy.deepcopy(my_payload)
        # 加过期时间
        payload['exp'] = time.time() + exp
        payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        payload_bs = Jwt.b64encode(payload_json.encode())
        # 使用key进行SHA256加密
        hm = hmac.new(key.encode(), header_bs + b'.' + payload_bs, digestmod='SHA256')
        hm_bs = Jwt.b64encode(hm.digest())
        return (header_bs + b"." + payload_bs + b"." + hm_bs).decode()

    @staticmethod
    def b64encode(j_s):
        return base64.urlsafe_b64encode(j_s).replace(b'=', b'')

    @staticmethod
    def my_decode(token_str, key):
        token = token_str.encode()
        header_bs, payload_bs, sign_bs = token.split(b'.')
        hm = hmac.new(key.encode(), header_bs + b'.' + payload_bs, digestmod='SHA256')
        if Jwt.b64encode(hm.digest()) != sign_bs:
            raise
        # 校验时间
        payload_json = Jwt.b64decode(payload_bs)
        # python3.6 loads可以转字节串
        payload = json.loads(payload_json)
        exp = payload['exp']
        if time.time() > exp:
            print('过期')
            raise Exception('过期')
        return payload

    @staticmethod
    def b64decode(b_s):
        rem = len(b_s) % 4
        b_s += b'=' * (4 - rem)
        return base64.urlsafe_b64decode(b_s)

# if __name__ == '__main__':
#     s = Jwt.my_encode({"id":"1","username": "13006370870"}, "0TLNWooggVcDzSkK")
#     print(s)
#     time.sleep(2)
#     res = Jwt.my_decode(s, '0TLNWooggVcDzSkK')
#     print(res)
#     '''
#         eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
#         eyJleHAiOjE1OTAyMjQ5NjAuNzU4ODksImlkIjoiMSIsInVzZXJuYW1lIjoiMTMwMDYzNzA4NzAifQ.
#         09hVHaJ5rANoG0Ss6BELlUM-4aPvuaxxN-BPCZZu5fg
#         {'exp': 1590224960.75889, 'id': '1', 'username': '13006370870'}
#     '''
