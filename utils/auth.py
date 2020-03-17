"""auth组件"""
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from app01 import models


class GeneralAuthentication(BaseAuthentication):
    '''
    通用认证，如果认证成功则返回数据，认证失败自己不处理，交给下一个组件处理
    '''

    def authenticate(self, request):

        token = request.META.get('HTTP_AUTHORIZATION', None)

        # 1. 如果用户没有 token 返回 None（意思是我不处理交给下一个组件处理，没有其他组件了 就默认返回None）
        if not token:
            return None

        # 2. token错误，返回None（意思是我不处理交给下一个组件处理，没有其他组件了 就默认返回None）
        user_obj = models.UserInfo.objects.filter(token=token).first()

        if not user_obj:
            return None
        # 3. 认证成功
        return (user_obj, token)  # user_obj就是request.user;token就是request.auth


class UserAuthentication(BaseAuthentication):
    '''
    用户认证
    '''

    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', None)

        # 1. 如果用户没有
        if not token:
            raise exceptions.AuthenticationFailed()

        # 2. token错误，
        user_obj = models.UserInfo.objects.filter(token=token).first()

        if not user_obj:
            raise exceptions.AuthenticationFailed()
        # 3. 认证成功
        return (user_obj, token)  # user_obj就是request.user;token就是request.auth
