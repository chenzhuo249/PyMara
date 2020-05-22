"""
{"code": 601, "error":"手机号不可用"}
{"code": 602, "error": "您的短信走丢了哦,再发一条试试吧!"}
{"code": 603, "error": "验证码校验失败"}
{"code": 604, "error": "用户注册失败(mysql create user error)"}
{"code": 605, "error": "用户注册失败,验证码校验失败"}
{"code": 606, "error": "用户登录失败,缺少账号或密码"}
{"code": 607, "error": "用户登录失败,账号或密码错误"}
{"code": 608, "error": "用户登录失败,账号不存在"}
{"code": 609, "error": "用户登录失败,账号或密码有误"}
{"code": 610, "error": "用户登录失败,用户账号状态异常"}
"""

import json
import re
import time
import random

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from user.models import User, Login
from django.conf import settings

from Public.message.send_msg import Message
from Public.message.send_email_465 import SendEmail
from django.db import transaction
from Public.publictoken import Jwt


class JudgePhoneNumber(View):

    def post(self, request):
        # return JsonResponse({"code":601, "error":"手机号不可用"})
        # return JsonResponse({"code":200, "data":"手机号可用"})

        phone_num_obj = json.loads(request.body.decode())
        phone_num = str(phone_num_obj["phone_number"])

        try:
            old_data = Login.objects.get(identifier=phone_num, method="2")
        except Exception as e:
            # 未查询到手机号的注册记录，手机号可以注册
            return JsonResponse({"code": 200, "data": "手机号可用"})

        # TODO 暂未校验用户的状态 现在是只要查到库里有这个手机号　就不允许注册
        return JsonResponse({"code": 601, "error":"手机号不可用"})


class SendMessage(View):

    """
        短信返回错误信息对应查询
        100	参数格式错误	检查请求参数是否为空, 或手机号码格式错误
        101	短信内容超过1000字	短信内容过长，请筛检或分多次发送
        105	appId错误或应用不存在	请联系工作人员申请应用或检查appId是否输入错误
        106	应用被禁止	请联系工作人员查看原因
        107	ip错误	如果设置了ip白名单，系统会检查请求服务器的ip地址，已确定是否为安全的来源访问
        108	短信余额不足	需要到用户中心进行充值
        109	今日发送超过限额	如果设置了日发送数量，则每个接收号码不得超过这个数量
        110	应用秘钥(AppSecret)错误	检查AppSecret是否输入错误，或是否已在用户中心进行了秘钥重置
        111	账号不存在	请联系工作人员申请账号
        1000 系统位置错误	请联系工作人员或技术人员检查原因
    """

    def create_random_number(self):
        return str(random.randint(100000, 999999))

    def send_error_email_to_manager(self, phone_num, code="xxx", data="未知问题"):
        dict_way = {
            100: "检查请求参数是否为空, 或手机号码格式错误",
            101: "短信内容过长，请筛检或分多次发送",
            105: "请联系工作人员申请应用或检查appId是否输入错误",
            106: "请联系工作人员查看原因",
            107: "如果设置了ip白名单，系统会检查请求服务器的ip地址，已确定是否为安全的来源访问",
            108: "需要到用户中心进行充值",
            109: "如果设置了日发送数量，则每个接收号码不得超过这个数量",
            110: "检查AppSecret是否输入错误，或是否已在用户中心进行了秘钥重置",
            111: "请联系工作人员申请账号",
            1000: "请联系工作人员或技术人员检查原因",
        }
        way = dict_way.get(code, "未知原因，请联系工作人员，迅速解决!")

        from_email = "1102225813@qq.com"
        from_pass = "evstyhswxsawjada"
        list_addrs = [("陈卓小号", "783753616@qq.com"),
                      ("袁祖亮", "1344748066@qq.com"),
                      ("李慧民", "527181835@qq.com"),
                      ("刘华兴", "669177285@qq.com"), ]
        error_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        email_text = """
            <h2>
                错误类型: 用户注册短信验证码服务器发送失败<br>
                错误时间: {}<br>
                注册账户: {}<br>
                错误代码: {}<br>
                错误原因: {}<br>
                解决方式: {}
            </h2> 
        """.format(error_time ,phone_num, code, data, way)

        email_obj = SendEmail(my_email=from_email, my_pass=from_pass, list_addr=list_addrs)
        res = email_obj.mail(email_text, "【PyMara报错邮件】")

        if res:
            print("注册报错邮件发送成功")
        else:
            print("注册报错邮件发送失败")

    def post(self, request):

        phone_num_obj = json.loads(request.body.decode())
        phone_num = str(phone_num_obj["phone_number"])
        ran_num = self.create_random_number()

        msh_obj = Message()
        res_str = msh_obj.send_message(phone_num, ran_num)

        res_obj = json.loads(res_str)

        # 测试节约短信验证码用
        # res_obj = {"code":0, "data":"发送成功"}
        # print(f"------- {ran_num} -------")

        code = res_obj["code"]
        data = res_obj["data"]

        if not code:
            # 在此处将验证码存入 redis,过期时间　300秒
            # TODO redis 方案一　需要修改
            import redis
            redis_15_key = "register:{}".format(phone_num)
            r = redis.Redis(db=15)
            r.set(name=redis_15_key, value=ran_num, ex=300)

            return JsonResponse({"code": 200, "data": "发送成功,请在手机端查收"})

        # 此时用户验证短信发送失败 自动发系统报错邮件 到管理员邮箱
        self.send_error_email_to_manager(phone_num, code, data)

        return JsonResponse({"code": 602, "error": "您的短信走丢了哦,再发一条试试吧!"})


class Register(View):

    def judge_msg_number(self, db, redis_15_key, msg_num):
        """
            校验用户验证码
        :param db: int redis 库名
        :param redis_15_key: str key
        :param msg_num: str 验证码
        :return:  True 校验成功  False 校验失败
        """
        # TODO redis 查询方式一 有可能修改
        import redis
        r = redis.Redis(db=db)
        result = r.get(redis_15_key)
        # 没查询到返回 None
        # 注意　None.decode() 会报错 AttributeError: 'NoneType' object has no attribute 'decode'
        # 找到则返回value的字节串 b'234453'

        if result:
            if msg_num == result.decode():
                return True
            return False
        return False

    def hash_md5_psd(self, psd):
        """
            将明文密码通过 md5算法转成密文存储
        :param psd: str 明文密码
        :return: str 转换后的密文密码
        """
        import hashlib
        m = hashlib.md5()
        m.update(psd.encode())  # 注意此处应是字节串
        return m.hexdigest()

    def post(self, request):

        msg_obj = json.loads(request.body.decode())
        str_msg_num = str(msg_obj["msg_num"])
        str_phone_num = str(msg_obj["phone_num"])

        redis_15_key = "register:{}".format(str_phone_num)

        if self.judge_msg_number(15, redis_15_key, str_msg_num):
            # 校验成功　可以写入数据库
            str_psd = str(msg_obj["psd"])
            uname = "py_{}".format(str_phone_num)
            hash_psd = self.hash_md5_psd(str_psd)

            # TODO 是否需要开事务
            # 开启事务
            with transaction.atomic():
                # 禁止自动提交
                save_id = transaction.savepoint() # 创建保存点,记录当前的状态
                try:
                    new_user = User.objects.create(username=uname)
                    new_user.login_set.create(method=2, identifier=str_phone_num, token=hash_psd)
                except Exception as e:
                    print("------- mysql create user error -------")
                    print(e)
                    transaction.savepoint_rollback(save_id) # 失败回滚
                    return JsonResponse({"code": 604, "error": "用户注册失败(mysql create user error)"})
                # 提交
                transaction.savepoint_commit(save_id)
                return JsonResponse({"code": 200, "data": "用户注册成功"})
        return JsonResponse({"code": 605, "error": "用户注册失败,验证码校验失败"})


class UserLogin(View):

    def judge_data(self, str_re, str_word):
        re_res = re.findall(str_re, str_word)
        if re_res and len(re_res) == 1 and re_res[0] == str_word:
            return True
        return False

    def post(self, request):
        user_obj = json.loads(request.body.decode())
        phone = user_obj.get("phone_number")
        psd = user_obj.get("password")

        if not phone or not psd:
            return JsonResponse({"code": 606, "error": "用户登录失败,缺少账号或密码"})

        # 后端校验数据
        if not self.judge_data(r"1[0-9]{10}", phone) and not self.judge_data(r"[0-9a-zA-Z_]{8,16}", psd):
            return JsonResponse({"code": 607, "error": "用户登录失败,账号或密码错误"})

        hash_psd = Register().hash_md5_psd(psd)
        try:
            old_psd = Login.objects.get(identifier=phone)
        except Exception as e:
            print("------Login get error------")
            print(e)
            return JsonResponse({"code": 608, "error": "用户登录失败,账号不存在"})
        # print("------status------")
        # print(old_psd.user.status, type(old_psd.user.status))
        # 0 <class 'int'>

        if hash_psd == old_psd.token:
            if old_psd.user.status == 0:
                # TODO 签发 token
                jwt_obj = Jwt()
                str_token = jwt_obj.my_encode({"id":old_psd.user.id, "phone":old_psd.identifier}, settings.JWT_TOKEN_KEY)
                return JsonResponse({"code": 200, "data": str_token})

            return JsonResponse({"code": 610, "error": "用户登录失败,用户账号状态异常"})

        return JsonResponse({"code": 609, "error": "用户登录失败,账号或密码有误"})



