from django.conf.urls import url
from app01.views import auth
from app01.views import topic
from app01.views import news
from app01.views import comment
from app01.views import auction

urlpatterns = [
    url(r'^login/', auth.LoginView.as_view()),
    url(r'^message/', auth.MessageView.as_view()),
    # 获取秘钥
    url(r'^credential/', auth.CredentialView.as_view()),

    # 发布动态 获取动态详细,点赞
    url(r'^news/', news.NewsView.as_view()),
    url(r'^newsdetail/(?P<pk>\d+)/$', news.NewsViewDetail.as_view()),
    url(r'^favor/', news.FavorView.as_view()),

    # 获取评论

    url(r'^comment/$', comment.CommentView.as_view()),

    # 获取话题
    url(r'^topic/', topic.TopicView.as_view()),

    # 拍卖专场
    url(r'^auction/$', auction.AuctionView.as_view()),
    # 拍卖详细页
    url(r'^auction/(?P<pk>\d+)/$', auction.AuctionDetailView.as_view()),
    # 单品详细
    url(r'^auction/item/(?P<pk>\d+)/$', auction.AuctionItemDetailView.as_view()),

    # '''继承GenericViewSet要写get对应的是啥'''
    # url(r'^auction2/$', auction.Auction2View.as_view({'get':'list'})),
    # url(r'^auction2/(?P<pk>\d+)/$', auction.Auction2View.as_view({'get':'retrieve'})),

]