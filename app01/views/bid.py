"""竞价"""
from app01 import models
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework import serializers

class BidModelSerializer(serializers.ModelSerializer):
    status_text = serializers.CharField(source='get_status_display', read_only=True)
    username = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = models.BidRecord
        fields = ['id', 'price', 'item', 'status_text', 'username']



# 竞价    GET: http://www.xxx.com/deposit/?item_id=1
# 提交竞价 POST: http://www.xxx.com/deposit/
class BidView(ListAPIView, CreateAPIView):
    queryset = models.BidRecord.objects.all().order_by('-id')
    serializer_class = BidModelSerializer

    def get_queryset(self):
        """
        获取传过来的值
        :return:
        """
        item_id = self.request.query_params.get('item_id')
        return self.queryset.filter(item_id=item_id)

    def get(self,request, *args, **kwargs):
        """
        页面两部分 上面的部分 加价，下面的部分是价格列表
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        response = super().get(request, *args, **kwargs)
        item_id = self.request.query_params.get('item_id')
        item_obj = models.AuctionItem.objects.filter(id=item_id).first()

        # 起拍价 item_obj.start_price
        # 出价记录最高价
        #   ① 倒序 取第一个      或者
        #   ② 当前单品的所有出价记录 models.BidRecord.objects.first(item_id=item_id) 在聚合一下  aggregate是取到一个值
        # models.BidRecord.objects.first(item_id=item_id).aggregate(max_price=Max('price'))是个字典
        from django.db.models import Max
        max_price = models.BidRecord.objects.filter(item_id=item_id).aggregate(max_price=Max('price'))['max_price']


        result = {
            'unit':item_obj.unit,
            'price':max_price or item_obj.start_price,
            'bit_list':response.data
        }
        response.data = result

        return response