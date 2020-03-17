import os
import sys
import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

# 将配置文件的路径写到 DJANGO_SETTINGS_MODULE 环境变量中
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "action_django.settings")
django.setup()

from app01 import models


def create_bid_record():
    models.BidRecord.objects.create(item_id=1,user_id=1,price=1000)
    models.BidRecord.objects.create(item_id=1,user_id=1,price=1200)
if __name__ == '__main__':
    create_bid_record()