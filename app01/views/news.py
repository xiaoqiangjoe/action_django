from app01 import models
from rest_framework import serializers
from django.forms import model_to_dict
from rest_framework.filters import BaseFilterBackend
# from rest_framework.pagination import LimitOffsetPagination
from django.db.models import F
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from utils.auth import GeneralAuthentication, UserAuthentication
# 分页
from utils.filters import MinFilterBackend, MaxFilterBackend
from utils.pagination import OldBoyLimitPagination


class CreateNewsTopicModelSerializer(serializers.Serializer):
    key = serializers.CharField()
    cos_path = serializers.CharField()


class CreateNewsModelSerializer(serializers.ModelSerializer):
    # 序列化的嵌套
    imageList = CreateNewsTopicModelSerializer(many=True)

    class Meta:
        model = models.News
        # fields = "__all__"
        exclude = ['user', 'viewer_count', 'comment_count']

    def create(self, validated_data):
        image_list = validated_data.pop("imageList")

        news_object = models.News.objects.create(**validated_data)
        data_list = models.NewsDetail.objects.bulk_create(
            [models.NewsDetail(**info, news=news_object) for info in image_list]
        )

        # 官方推荐 再返回一份
        news_object.imageList = data_list

        if news_object.topic:
            news_object.topic.count += 1
            news_object.save()

        return news_object


class ListNewsModelSerializer(serializers.ModelSerializer):
    # 因为这个样子是拿到的 tpoic和user 是一个数字 我们不希望是这样 所有我们修改
    user = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()

    class Meta:
        model = models.News
        fields = ['id', 'cover', 'content', 'topic', "user", "comment_count"]

    def get_user(self, obj):
        # return obj.user.nickname
        # return {'nickname',obj.user.nickname}
        # from django.forms import model_to_dict
        return model_to_dict(obj.user, fields=['id', 'nickname', 'avatar'])

    def get_topic(self, obj):
        if not obj.topic:
            return
        # from django.forms import model_to_dict
        return model_to_dict(obj.topic, fields=['id', 'title'])

"""utils里"""
# class OldBoyLimitPagination(LimitOffsetPagination):
#     """
#     本质上帮助我们进行切片的处理：[0:N]
#     """
#     default_limit = 5
#     max_limit = 50
#     limit_query_param = 'limit'
#     offset_query_param = 'offset'
#
#     def get_offset(self, request):
#         return 0
#
#     def get_paginated_response(self, data):
#         return Response(data)


# class MinFilterBackend(BaseFilterBackend):
#     def filter_queryset(self, request, queryset, view):
#         min_id = request.query_params.get('minId')
#         if not min_id:
#             return queryset
#         return queryset.filter(id__lt=min_id)[0:10]
#
#
# class MaxFilterBackend(BaseFilterBackend):
#     def filter_queryset(self, request, queryset, view):
#         max_id = request.query_params.get('maxId')
#         if not max_id:
#             return queryset
#         return queryset.filter(id__gt=max_id).reverse()


# #####################首页动态###############################
class NewsView(CreateAPIView, ListAPIView):
    serializer_class = CreateNewsModelSerializer
    queryset = models.News.objects.all().order_by('-id')

    pagination_class = OldBoyLimitPagination
    filter_backends = [MinFilterBackend, MaxFilterBackend]

    def perform_create(self, serializer):
        new_object = serializer.save(user_id=1)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateNewsModelSerializer
        if self.request.method == 'GET':
            return ListNewsModelSerializer


# #####################上面都是首页动态###############################


# #####################首页动态详细 开始 ###############################
# RetrieveAPIView 内部自动给我取传过来的值

class NewsModelViewDetail(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()

    create_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    images = serializers.SerializerMethodField()

    viewer = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()

    is_favor = serializers.SerializerMethodField()

    class Meta:
        model = models.News
        exclude = ['cover', ]

    def get_user(self, obj):
        return model_to_dict(obj.user, fields=['id', 'nickname', 'avatar'])

    def get_topic(self, obj):
        if not obj.topic:
            return
        return model_to_dict(obj.topic, fields=['id', 'title'])

    def get_images(self, obj):
        detail_queryset = models.NewsDetail.objects.filter(news=obj)

        # return [{'id':item.id,'path':item.cos_path} for item in detail_queryset]
        # return [item.cos_path for item in detail_queryset]
        return [model_to_dict(item, fields=['id', 'cos_path']) for item in detail_queryset]

    def get_viewer(self, obj):

        ''''要统计浏览人的总个数 你可以自己一个一个加到数据库，也可以像下面没有注释的方法'''
        # 根据动态的对象 obj（news）
        # viewer_query = models.ViewerRecord.objects.filter(news=obj).order_by("-id")[0:10]
        # return [model_to_dict(item.user, fields=['nickname', 'avatar']) for item in viewer_query]


        queryset = models.ViewerRecord.objects.filter(news=obj)
        viewer_list = queryset.order_by('-id')[0:10]
        context = {
            'count': queryset.count(),
            'result': [model_to_dict(item.user, fields=['nickname', 'avatar']) for item in viewer_list]
        }

        return context

    def get_comment(self, obj):
        '''
        获取评论的第一条评论，在获取每个评论的第一条二级评论
        :param obj:
        :return:
        '''

        # 1.首先获取所有的一级评论   下面可以用model_to_dict  也可以直接取 value
        first_queryset = models.CommentRecord.objects.filter(news=obj, depth=1).order_by('-id').values(
            'id',
            'content',
            'depth',
            'user__nickname',
            'user__avatar',
            'create_date',
        )

        # 2. 获取二级评论的所有评论
        '''
        second_queryset = models.CommentRecord.objects.filter(news=obj, depth=2).order_by('-id').values(
            'id',
            'content',
            'user__nickname',
            'user__avatar',
            'create_date'
        ) 
        # 2. 获取一级评论下的 二级评论
        # first_id_list = [item['id'] for item in first_queryset]
        # second_queryset = models.CommentRecord.objects.filter(news=obj, depth=2, reply_id__in=first_id_list).order_by('-id').values('id','content','user__nickname','user__avatar','create_date')
        '''
        # 2. 获取一级评论下的 二级评论(每个二级评论只取最新的一条)
        # 获取一级评论的 id
        first_id_list = [item['id'] for item in first_queryset]

        from django.db.models import Max

        # 到 values处 就是先取出一级评论下的所有二级评论，在取一个最大的  就是分组取最大
        result = models.CommentRecord.objects.filter(news=obj, depth=2, reply_id__in=first_id_list).values(
            'reply_id').annotate(max_id=Max('id'))

        second_id_list = [item['max_id'] for item in result]  # 5, 8

        # 获取二级评论
        second_queryset = models.CommentRecord.objects.filter(id__in=second_id_list).values(
            'id',
            'content',
            'depth',
            'user__nickname',
            'user__avatar',
            'create_date',
            'reply_id',
            'reply__user__nickname',
        )
        '''这个时候我们把第一级评论和第二级评论合并  请看脚本 处理评论结构化
        1. 字典的有序
        2. 看下面代码
        '''
        import collections
        first_dict = collections.OrderedDict()

        first_dict = {}
        for item in first_queryset:
            # print(item)
            item['create_date'] = item['create_date'].strftime('%Y-%m-%d')
            item['child'] = []
            first_dict[item['id']] = item

        for node in second_queryset:
            node['create_date'] = node['create_date'].strftime('%Y-%m-%d %H:%M:%S')
            first_dict[node['reply_id']]['child'] = [node, ]
        # print('first_dict',first_dict)
        return first_dict.values()
        '''
        {
    "id": 40,
    "user": {
        "id": 1,
        "nickname": "1",
        "avatar": null
    },
    "topic": {
        "id": 1,
        "title": "春运"
    },
    "create_date": "2020-03-11 14:01:30",
    "images": [
        {
            "id": 8,
            "cos_path": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/qd8uqha71583935212904.png"
        },
        {
            "id": 9,
            "cos_path": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/dyc0v9bj1583935213072.png"
        },
        {
            "id": 10,
            "cos_path": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/4bk1t5jz1583935213114.png"
        },
        {
            "id": 11,
            "cos_path": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/neepezyd1583935213147.png"
        },
        {
            "id": 12,
            "cos_path": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/us8dvkfb1583935213159.png"
        },
        {
            "id": 13,
            "cos_path": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/9umlmob51583935213171.png"
        },
        {
            "id": 14,
            "cos_path": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/qfstmdlr1583935213192.png"
        },
        {
            "id": 15,
            "cos_path": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/2ik3hayk1583935213204.png"
        },
        {
            "id": 16,
            "cos_path": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/beeo2s5t1583935213215.png"
        }
    ],
    "viewer": {
        "count": 8,
        "result": [
            {
                "nickname": "晓强3",
                "avatar": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/qd8uqha71583935212904.png"
            },
            {
                "nickname": "晓强4",
                "avatar": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/qd8uqha71583935212904.png"
            },
            {
                "nickname": "晓强15",
                "avatar": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/qd8uqha71583935212904.png"
            },
            {
                "nickname": "晓强13",
                "avatar": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/qd8uqha71583935212904.png"
            },
            {
                "nickname": "晓强2",
                "avatar": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/qd8uqha71583935212904.png"
            },
            {
                "nickname": "晓强11",
                "avatar": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/qd8uqha71583935212904.png"
            },
            {
                "nickname": "晓强0",
                "avatar": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/qd8uqha71583935212904.png"
            },
            {
                "nickname": "1",
                "avatar": null
            }
        ]
    },
    "comment": [
        {
            "id": 21,
            "content": "3",
            "user__nickname": "晓强2",
            "user__avatar": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/qd8uqha71583935212904.png",
            "create_date": "2020-03-12T14:45:43.062687Z"
        },
        {
            "id": 20,
            "content": "2",
            "user__nickname": "晓强1",
            "user__avatar": "http://upload-1301374893.cos.ap-chengdu.myqcloud.com/qd8uqha71583935212904.png",
            "create_date": "2020-03-12T14:45:42.934679Z"
        },
        {
            "id": 15,
            "content": "1",
            "user__nickname": "1",
            "user__avatar": null,
            "create_date": "2020-03-12T14:45:41.652606Z",
            "child": [
                {
                    "reply_id": 15,
                    "max_id": 19
                }
            ]
        }
    ],
    "content": "首页和发布页面写完了",
    "address": "北京市昌平区政府街",
    "favor_count": 0,
    "viewer_count": 0,
    "comment_count": 0
}
        '''

    def get_is_favor(self, obj):
        # 1. 用户是否登录
        user_obj = self.context['request'].user
        if not user_obj:
            return False
        exsits = models.NewsFavorRecord.objects.filter(user=user_obj, news=obj).exists()
        if exsits:
            return True
        else:
            return False


class NewsViewDetail(RetrieveAPIView):
    queryset = models.News.objects
    serializer_class = NewsModelViewDetail
    # 如果想全局的话就在全局设置
    # authentication_classes = [GeneralAuthentication,]

    def get(self,request, *args, **kwargs):
        response = super().get(self,request, *args, **kwargs)
        '''上面两行代码+return response 就是啥也没有做，但是可以在中间加功能'''
        # 获取token
        # from rest_framework.authentication import     在Django中获取请求头是在META中 必须写成 HTTP_加字段的大写
        '''
        token = request.META.get('HTTP_AUTHORIZATION', None)
        if not token:
            return response

        user_obj = models.UserInfo.objects.filter(token=token).first()

        if not user_obj:
            return response
        '''
        # 默认是一个匿名用户，但是我们设置一个没有返回None  在settings
        if not request.user:
            return response

        '''上面是获取token，下面的做数据库操作，访问记录'''
        # 如果有 我们就填写访问记录
        # 父类内部给做的 有就进行 没有就捕获错误
        news_obj = self.get_object()       # models.News.object.get(pk=pk)

        viewerrecord_exists = models.ViewerRecord.objects.filter(user=request.user, news=news_obj).exists()

        if viewerrecord_exists:
            return response

        models.ViewerRecord.objects.create(user=request.user, news=news_obj)
        models.News.objects.filter(id=news_obj.id).update(viewer_count=F('viewer_count')+1)

        return response


# ###################文章点赞接口########################

class FavorModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NewsFavorRecord
        fields = ['news']



class FavorView(APIView):
    authentication_classes = [UserAuthentication, ]

    def post(self, request, *args, **kwargs):

        ser = FavorModelSerializer(data=request.data)

        if not ser.is_valid():
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        news_obj = ser.validated_data.get('news')

        queryset = models.NewsFavorRecord.objects.filter(user=request.user, news=news_obj)
        exists = queryset.exists()

        if exists:
            queryset.delete()
            return Response({}, status=status.HTTP_200_OK)
        models.NewsFavorRecord.objects.create(user=request.user, news=news_obj)
        return Response({}, status=status.HTTP_201_CREATED)




