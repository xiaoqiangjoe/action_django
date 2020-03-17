from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from utils.auth import GeneralAuthentication, UserAuthentication
from rest_framework import serializers
from django.forms import model_to_dict
from app01 import models
from rest_framework import status
from django.db.models import F


'''
class CommenModelSerializert(serializers.ModelSerializer):
    create_date = serializers.DateTimeField('%Y-%m-%d')
    user = serializers.SerializerMethodField()
    reply_user = serializers.SerializerMethodField()

    class Meta:
        model = models.CommentRecord
        fields = '__all__'

    def get_user(self, obj):
        return model_to_dict(obj.user, fields=['id', 'nickname', 'avatar'])

    def get_reply_user(self, obj):
        return model_to_dict(obj.reply.user, fields=['id', 'nickname'])

'''
class CommenModelSerializert(serializers.ModelSerializer):
    create_date = serializers.DateTimeField('%Y-%m-%d')
    user__nickname = serializers.CharField(source='user.nickname')
    user__avatar = serializers.CharField(source='user.avatar')
    reply_id = serializers.CharField(source='reply.id')
    reply__user__nickname = serializers.CharField(source='reply.user.nickname')

    class Meta:
        model = models.CommentRecord
        # fields = '__all__'
        exclude = ['news', 'user', 'reply', 'root']



class CreateCommenModelSerializert(serializers.ModelSerializer):
    create_date = serializers.DateTimeField('%Y-%m-%d', read_only=True)
    user__nickname = serializers.CharField(source='user.nickname', read_only=True)
    user__avatar = serializers.CharField(source='user.avatar', read_only=True)
    reply_id = serializers.CharField(source='reply.id', read_only=True)
    reply__user__nickname = serializers.CharField(source='reply.user.nickname', read_only=True)

    class Meta:
        model = models.CommentRecord
        # fields = '__all__'
        exclude = ['user', 'favor_count']



class CommentView(APIView):

    # 重写源码的这个方法
    def get_authenticators(self):
        if self.request.method == 'POST':
            return [UserAuthentication,]
        return [GeneralAuthentication,]

    def get(self, request, *args, **kwargs):
        root_id = request.query_params.get('root_id')

        comment_query = models.CommentRecord.objects.filter(root_id=root_id).order_by('id')

        ser = CommenModelSerializert(instance=comment_query, many=True)

        return Response(ser.data)

    def post(self, request, *args, **kwargs):

        # 1.进行数据校验    序列化 news/ depth/reply/content/root
        ser = CreateCommenModelSerializert(data=request.data)
        # 2.校验通过 保存数据库
        if ser.is_valid():
            # 保存到数据库
            ser.save(user_id=1)
            # 对新增的数据值进行序列化【数据格式要调整 参考上面的read_only创建的时候校验，传过去不校验】
            print(ser.data)
            new_id= ser.data.get('news')
            models.News.objects.filter(id=new_id).update(comment_count=F('comment_count')+1)
            return Response(ser.data,status=status.HTTP_201_CREATED)
        return Response(ser.errors)
        # 3.将保存到数据库的数据再返回小程序页面（小程序页面要展示）


