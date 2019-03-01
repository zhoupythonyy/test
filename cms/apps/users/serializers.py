import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from users.models import User, Address


class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.BooleanField(label='同意协议', write_only=True)

    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self, value):
        """检验用户是否同意协议"""
        if not value:
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一致')

        # 判断短信验证码
        redis_conn = get_redis_connection('sms_codes')
        mobile = attrs['mobile']
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if attrs['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')

        return attrs

    def create(self, validated_data):
        user =  User.objects.create_user(
            username=validated_data.get('username'),
            password=validated_data.get('password'),
            mobile=validated_data.get('mobile'))
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token  # 生成的jwt 序列化返回
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2',
                  'sms_code', 'mobile', 'allow')

    extra_kwargs = {
        'username': {
            'min_length': 5,
            'max_length': 20,
            'error_messages': {
                'min_length': '仅允许5-20个字符的用户名',
                'max_length': '仅允许5-20个字符的用户名',
            }
        },
        'password': {
            'write_only': True,
            'min_length': 8,
            'max_length': 20,
            'error_messages': {
                'min_length': '仅允许8-20个字符的密码',
                'max_length': '仅允许8-20个字符的密码',
            }
        }
    }


class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器: 序列化 + 校验参数
    """
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)

    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        """ 保存 """
        # 补充一个字段： 收件地址所属用户, 再保存到数据库表中
        validated_data['user'] = self.context['request'].user  # 获取当前登录用户对象
        return super().create(validated_data)

    class Meta:
        model = Address
        # 新增地址，不需要用户传递user到服务器，服务器可以自动获取到当前登录用户对象
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')