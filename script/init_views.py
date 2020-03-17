'''浏览记录表'''
import os
import sys
import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

# 将配置文件的路径写到 DJANGO_SETTINGS_MODULE 环境变量中
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "action_django.settings")
django.setup()

from app01 import models

models.ViewerRecord.objects.create(user_id=1, news_id=40)
models.ViewerRecord.objects.create(user_id=2, news_id=40)
models.ViewerRecord.objects.create(user_id=13, news_id=40)
models.ViewerRecord.objects.create(user_id=4, news_id=40)
models.ViewerRecord.objects.create(user_id=15, news_id=40)
models.ViewerRecord.objects.create(user_id=17, news_id=40)
models.ViewerRecord.objects.create(user_id=6, news_id=40)
models.ViewerRecord.objects.create(user_id=5, news_id=40)

