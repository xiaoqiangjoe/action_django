import os
import sys
import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

# 将配置文件的路径写到 DJANGO_SETTINGS_MODULE 环境变量中
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "action_django.settings")
django.setup()

from app01 import models
import datetime
from datetime import timedelta



def create_auction():
    current_datetime = datetime.datetime.now()
    '''
    一个专场  Auction
    '''
    auction_object = models.Auction.objects.create(
        title='第一场 烟酒',
        cover="https://auction-1251317460.cos.ap-chengdu.myqcloud.com/23bf0e42-d9ff-44a4-9418-1b9e01ebbb61.png",
        preview_start_time=current_datetime,
        preview_end_time=current_datetime + timedelta(hours=5),
        auction_start_time=current_datetime + timedelta(hours=5),
        auction_end_time=current_datetime + timedelta(hours=7),
        deposit=1200,
        goods_count=2
    )
    '''
    一个拍品 AuctionItem  三张图片  两个规格
    '''
    item1_object = models.AuctionItem.objects.create(
        auction=auction_object,
        uid="202011111111",
        title='茅台',
        cover="https://auction-1251317460.cos.ap-chengdu.myqcloud.com/23bf0e42-d9ff-44a4-9418-1b9e01ebbb61.png",
        start_price=1499,
        reserve_price=1000,
        highest_price=2800,
        deposit=200,
        unit=100
    )

    image1_object = models.AuctionItemImage.objects.create(
        item=item1_object,
        img="https://auction-1251317460.cos.ap-chengdu.myqcloud.com/23bf0e42-d9ff-44a4-9418-1b9e01ebbb61.png",
        carousel=True,
        order=1
    )
    image2_object = models.AuctionItemImage.objects.create(
        item=item1_object,
        img="https://auction-1251317460.cos.ap-chengdu.myqcloud.com/23bf0e42-d9ff-44a4-9418-1b9e01ebbb61.png",
        carousel=True,
        order=2
    )
    image3_object = models.AuctionItemImage.objects.create(
        item=item1_object,
        img="https://auction-1251317460.cos.ap-chengdu.myqcloud.com/23bf0e42-d9ff-44a4-9418-1b9e01ebbb61.png",
        carousel=False,
        order=3
    )

    detail1_object = models.AuctionItemDetail.objects.create(item=item1_object,key='品牌',value='茅台')
    detail2_object = models.AuctionItemDetail.objects.create(item=item1_object, key='年份', value='1800')


def create_bid_record():
    models.BidRecord.objects.create(item_id=1,user_id=1,price=1000)
    models.BidRecord.objects.create(item_id=1,user_id=1,price=1200)
if __name__ == '__main__':
    create_auction()
    # create_bid_record()