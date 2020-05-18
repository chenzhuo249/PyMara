"""
登录令牌
"""

import copy
import json
import base64
import time
import hmac


class Jwt:
    def __init__(self):
        pass

    @staticmethod
    def encode(my_payload, key, exp=3600 * 24):
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
    def decode(token_str, key):
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
#     s = Jwt.encode({"username": "xiaoguaishou"}, "abcdef")
#     print(s)
#     # time.sleep(4)
#     res = Jwt.decode(s, 'abcdef')
#     print(res)
#     '''
#      eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
#      .eyJleHAiOjE1ODY1MDkwMjcuNTY1NjQzLCJ1c2VybmFtZSI6InhpYW9ndWFpc2hvdSJ9
#      .gBcf3zzlqXoKWh_tG0JwkgtQu2aVCUziTTSHRXnus4Q
#     '''
