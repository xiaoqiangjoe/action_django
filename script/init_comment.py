import os
import sys
import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

# 将配置文件的路径写到 DJANGO_SETTINGS_MODULE 环境变量中
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "action_django.settings")
django.setup()

from app01 import models

'''
形式：
1
    1-1
        1-1-1
        1-1-2
    1-2
2
3

'''

# 第一条一级评论
first1 = models.CommentRecord.objects.create(
    news_id=40,
    content="1",
    user_id=1,
    depth=1
)
# 第一条一级评论的第一条子评论
first1_1 = models.CommentRecord.objects.create(
    news_id=40,
    content="1-1",
    user_id=6,
    reply=first1,
    depth=2,
    root=first1
)
# 第一条一级评论的第一条子评论的再评论
first1_1_1 = models.CommentRecord.objects.create(
    news_id=40,
    content="1-1-1",
    user_id=10,
    reply=first1_1,
    depth=3,
    root=first1
)
# 第一条一级评论的第一条子评论的再评论
first1_1_2 = models.CommentRecord.objects.create(
    news_id=40,
    content="1-1-2",
    user_id=14,
    reply=first1_1,
    depth=3,
    root=first1
)
# 第一条一级评论的第二条子评论
first1_2 = models.CommentRecord.objects.create(
    news_id=40,
    content="1-2",
    user_id=8,
    reply=first1,
    depth=2,
    root=first1
)

# 第二条一级评论
first2 = models.CommentRecord.objects.create(
    news_id=40,
    content="2",
    user_id=3,
    depth=1
)

# 第三条一级评论
first3 = models.CommentRecord.objects.create(
    news_id=40,
    content="3",
    user_id=4,
    depth=1
)
