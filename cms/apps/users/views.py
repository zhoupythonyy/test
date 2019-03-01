from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users import serializers
from users.models import User


class UsernameCountView(APIView):
    """判断用户名是否重复"""
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        return Response(data)


class SMSCodeView(APIView):
    """发送短信验证码"""

    def get(self, request, mobile):
        # 获取StrictRedis保存数据
        strict_redis = get_redis_connection('sms_codes')  # type: StrictRedis

        send_flag = strict_redis.get('send_flag_%s' % mobile)
        if send_flag:
            raise ValidationError({'message': '发送短信过于频繁'})

        # 1. 生成短信验证码
        import random
        sms_code = '%06d' % random.randint(0, 999999)
        print("短信验证码：", sms_code)
        # 2. 使用云通讯发送短信验证码
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)

        # 3. 保存短信验证码到Redis expiry
        strict_redis.setex('sms_%s' % mobile, 5 * 60, sms_code)  # 5分钟
        strict_redis.setex('send_flag_%s' % mobile, 60, 1)  # 1分钟过期

        return Response({'message': 'ok'})


class UserView(CreateAPIView):
    """用户注册"""
    serializer_class = serializers.CreateUserSerializer