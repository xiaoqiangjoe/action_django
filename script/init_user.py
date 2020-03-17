
import os
import sys
import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

# 将配置文件的路径写到 DJANGO_SETTINGS_MODULE 环境变量中
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "action_django.settings")
django.setup()

from app01 import models
for i in range(20):
    models.UserInfo.objects.create(
        telephone="15311445555",
        nickname="晓强{0}".format(i),
        avatar="http://upload-1301374893.cos.ap-chengdu.myqcloud.com/qd8uqha71583935212904.png")













