from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django_redis import get_redis_connection

from app01.serializer.validators import phone_validator


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(label="手机号", validators=[phone_validator, ])
    code = serializers.CharField(label="验证码")
    nickname = serializers.CharField(label='昵称')
    avatar = serializers.CharField(label='头像')

    def validate_code(self, value):
        '''
        校验验证码
        :param value:
        :return:
        '''
        if len(value) != 4:
            raise ValidationError('短信格式错误')
        if not value.isdecimal():
            raise ValidationError('短信格式错误')

        '''
        initial_data 在这样必须用 initial_data相当于request.data 
        对比一下 is_valid中validated_data
        '''
        phone = self.initial_data.get('phone')
        # code验证
        conn = get_redis_connection()
        code = conn.get(phone)
        if not code:
            raise ValidationError('验证码过期')
        if value != code.decode('utf-8'):
            raise ValidationError('验证码过期')
        return value


class MessageSerializer(serializers.Serializer):
    '''
    只是默认验证phone不为空 自己要是想加验证 自己加一个 validators 还可以钩子校验
    顺序 先校验默认不为空，在校验validators 在校验钩子函数
    '''
    phone = serializers.CharField(label="手机号", validators=[phone_validator, ])
