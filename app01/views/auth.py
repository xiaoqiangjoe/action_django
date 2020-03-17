import uuid
import json
import os

from rest_framework.views import APIView
from rest_framework.response import Response
from django_redis import get_redis_connection
from app01.serializer.auth import MessageSerializer, LoginSerializer
from app01 import models

from utils.tencent.msg import send_message
from sts.sts import Sts

# Create your views here.


'''
class MessageSerializer(serializers.ModelSerializer):
    """
    这段代码是我们在有表的时候使用的 现在没有表 我们用继承serializers.Serializer
    下面的class Meta也不能要了
    """
    class Meta:
        model = "表"
        fileds = "__all__"
'''


class MessageView(APIView):
    def get(self, request, *args, **kwargs):
        '''
        获取手机号
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''

        '''
        1. 获取手机号
        2. 手机格式校验
        3. 生成随机验证码
        4. 验证码发送到手机上
        5. 把验证码+手机号保留（30s过期）

            用redis做conn.set("13811091111","1459",ex=30)
            conn.get("13811091111")获取验证码 再和用户对比
        '''
        # 1. 获取手机号
        # phone = request.query_params.get('phone')
        # print('phone',phone)

        #  2. 手机格式校验
        # ①
        '''
        import re
        if not re.match(r'^(1[3|4|5|6|7|8|9])\d{9}$',phone):
            return Response("手机号格式错误")
        '''
        # ②
        ser = MessageSerializer(data=request.query_params)

        if not ser.is_valid():
            return Response({'status': False, 'message': '手机号格式错误'})

        phone = ser.validated_data.get("phone")

        # 3. 生成随机验证码
        import random
        random_code = random.randint(1000, 9999)
        print('82行random_code', random_code)

        # 4. 验证码发送到手机上 购买服务器进行发送短信；阿里云/ 腾讯云
        ''' 
        result = send_message(phone, random_code)
        if not result:
            return Response({"status": False, 'message': '短信发送失败'})
        '''
        # 5. 把验证码+手机号保留（30s过期）
        # 5.1 搭建redis  腾讯云 阿里云  也有
        # 5.2 django-redis
        # from django_redis import get_redis_connection
        conn = get_redis_connection()
        conn.set(phone, random_code, ex=60)
        return Response({"status": True, "message": '发送成功'})


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        '''
        1. 校验手机号是否合法
        2. 校验验证码 redis
            - 无验证码
            - 有验证码 输入错误
            - 有验证码 输入成功
        3. 去数据库中获取用户信息（获取/创建）
        4. 将一些信息返回给小程序
        '''

        ser = LoginSerializer(data=request.data)
        if not ser.is_valid():
            return Response({"status": False, 'message': '验证码错误'})

        phone = ser.validated_data.get('phone')
        nickname = ser.validated_data.get('nickname')
        avatar = ser.validated_data.get('avatar')
        print(phone,nickname,avatar)
        ''' 
        user = models.UserInfo.objects.filter(phone=phone).first()
        if not user:
            models.UserInfo.objects.create(phone=phone,token=str(uuid.uuid4()))
        else:
            user.token = uuid.uuid4()
            user.save()
        '''


        user_object, flag = models.UserInfo.objects.get_or_create(
            telephone=phone,
            defaults={
                'avatar':avatar,
                'nickname':nickname
            }
        )
        user_object.token = str(uuid.uuid4())
        user_object.save()
        return Response({"status": True, 'data': {'phone': phone, 'token': user_object.token}})


class CredentialView(APIView):
    def get(self, request, *agrs, **kwargs):
        config = {
            # 临时密钥有效时长，单位是秒
            'duration_seconds': 1800,

            '''

            'secret_id': 
            ❤ 缺两行代码
            'secret_key': 
            '''

            # 设置网络代理
            # 'proxy': {
            #     'http': 'xx',
            #     'https': 'xx'
            # },
            # 换成你的 bucket
            'bucket': 'upload-1301374893',
            # 换成 bucket 所在地区
            'region': 'ap-chengdu',
            # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
            # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
            'allow_prefix': '*',
            # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
            'allow_actions': [
                # 简单上传
                # 'name/cos:PutObject',
                'name/cos:PostObject',
                'name/cos:DeleteObject',
                # 分片上传
                # 'name/cos:InitiateMultipartUpload',
                # 'name/cos:ListMultipartUploads',
                # 'name/cos:ListParts',
                # 'name/cos:UploadPart',
                # 'name/cos:CompleteMultipartUpload'
            ],

        }

        # try:
        sts = Sts(config)
        response = sts.get_credential()
        print('get data : ' + json.dumps(dict(response), indent=4))
        # except Exception as e:
        #     print(e)

        return Response(response)
