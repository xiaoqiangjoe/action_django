from app01 import models
from django.forms import model_to_dict
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework import serializers
from utils.filters import MinFilterBackend, MaxFilterBackend
from utils.pagination import OldBoyLimitPagination


# ##############拍卖专场接口###################################
class AuctionModelSerializerView(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    preview_start_time = serializers.DateTimeField(format="%Y-%m-%d")

    goods = serializers.SerializerMethodField()

    class Meta:
        model = models.Auction
        # fields = "__all__"
        fields = ['id', 'title', 'cover', 'status', 'preview_start_time',
                  'look_count', 'goods_count', 'total_price', 'bid_count', 'goods']

    def get_goods(self, obj):
        queryset = models.AuctionItem.objects.filter(auction=obj)[0:5]
        return [row.cover for row in queryset]


class AuctionView(ListAPIView):
    """
    拍卖专场接口
    """
    # queryset = models.Auction.objects.filter(status__gt=1).order_by('id')
    queryset = models.Auction.objects.filter(status__gt=0).order_by('id')
    serializer_class = AuctionModelSerializerView
    # 分页接口
    filter_backends = [MinFilterBackend, MaxFilterBackend]
    pagination_class = OldBoyLimitPagination


# #######拍卖列表详细页面 专场详细##########################################

class AuctionDetailItemModelSerializer(serializers.ModelSerializer):
    is_deposit = serializers.SerializerMethodField()

    class Meta:
        model = models.AuctionItem
        fields = ['id', 'cover', 'status', 'reserve_price', 'highest_price', 'is_deposit']

    def get_is_deposit(self, obj):
        user_object = self.context['request'].user
        if not user_object:
            return False
        return models.DepositRecord.objects.filter(user=user_object, item=obj, status=2, deposit_type=1).exists()


class AuctionModelDetailView(serializers.ModelSerializer):
    goods = serializers.SerializerMethodField()
    # 检查是否缴纳保证金
    is_deposit = serializers.SerializerMethodField()

    model = models.Auction
    fields = '__all__'

    def get_goods(self, obj):
        # 每个单品信息
        item_object_list = models.AuctionItem.objects.filter(auction=obj)
        ser = AuctionDetailItemModelSerializer(instance=item_object_list, many=True, context=self.context)
        return ser.data

    def get_is_deposit(self, obj):
        """ 检查是否已缴纳全场保证金 """
        # 1. 没登陆，显示去缴纳保证金
        user_object = self.context['request'].user
        if not user_object:
            return False
        # 2. 去查看缴纳保证金记录的表中是否有此用户&此专场
        return models.DepositRecord.objects.filter(user=user_object, auction=obj, status=2, item__isnull=True).exists()


class AuctionDetailView(RetrieveAPIView):
    """
    拍卖列表详细页面 专场详细
    """
    queryset = models.Auction.objects.filter(status__gt=1)
    serializer_class = AuctionModelDetailView


#############整合两个接口#####################################33

'''
class Auction2View(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = models.Auction.objects.filter(status__gt=1).order_by('-id')
    serializer_class = AuctionModelSerializerView
    filter_backends = [MinFilterBackend, MaxFilterBackend, ]
    pagination_class = OldBoyLimitPagination

    def get_serializer_class(self):
        pk = self.kwargs.get('pk')
        if pk:
            return AuctionModelDetailView
        return AuctionModelSerializerView
'''


#############单品详细#####################################33
class AuctionItemDetailModelSerializer(serializers.ModelSerializer):
    """
    轮播图，图片，规格，浏览记录
    """
    carousel_list = serializers.SerializerMethodField()
    detail_list = serializers.SerializerMethodField()
    image_list = serializers.SerializerMethodField()
    record = serializers.SerializerMethodField()

    class Meta:
        model = models.AuctionItem
        fields = "__all__"

    def get_carousel_list(self, obj):
        queryset = models.AuctionItemImage.objects.filter(item=obj, carousel=True).order_by('-order')
        return [row.img for row in queryset]

    def get_image_list(self, obj):
        queryset = models.AuctionItemImage.objects.filter(item=obj).order_by('-order')
        return [row.img for row in queryset]

    def get_detail_list(self, obj):
        queryset = models.AuctionItemDetail.objects.filter(item=obj)
        return [model_to_dict(row, ['key', 'value']) for row in queryset]

    def get_record(self, obj):
        queryset = models.BrowseRecord.objects.filter(item=obj)
        result = {
            'record_list': [row.user.avatar for row in queryset[0:10]],
            'total_count': queryset.count()
        }
        return result


# 单品详细
class AuctionItemDetailView(RetrieveAPIView):
    queryset = models.AuctionItem.objects.filter(status__gt=1)
    serializer_class = AuctionItemDetailModelSerializer


# ##########保证金#########################################

class AuctionDepositModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AuctionItem
        fields = '__all__'



class AuctionDepositlView(RetrieveAPIView):
    queryset = models.AuctionItem.objects.filter(status__in=[2,3])
