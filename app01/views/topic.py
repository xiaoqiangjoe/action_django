from rest_framework.generics import ListAPIView
from rest_framework.serializers import ModelSerializer

from .. import models


class TopicViewModelSerializer(ModelSerializer):
    class Meta:
        model = models.Topic
        fields = "__all__"

class TopicView(ListAPIView):
    serializer_class = TopicViewModelSerializer
    queryset = models.Topic.objects.all().order_by("-count")