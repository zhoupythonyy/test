from django_redis import get_redis_connection
from rest_framework import mixins
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from users import serializers
from users.models import User, Address


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


class AddressView(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin,mixins.UpdateModelMixin,
                  GenericViewSet):
    """用户地址管理"""
    serializer_class = serializers.UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """获取当前用户地址"""
        return self.request.user.addresses.filter(is_deleted=False)

    def list(self, request, *args, **kwargs):
        """ 用户地址列表数据 """
        # 当前登录用户的所有地址
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'user_id': request.user.id,
            'default_address_id': request.user.default_address_id,
            'addresses': serializer.data
            })

    def update(self, request, *args, **kwargs):
        """设置默认地址"""
        address = self.get_object()
        address.user.default_address_id = address.id
        address.user.save()
        return Response(self.get_serializer(address).data)
