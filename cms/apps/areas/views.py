from rest_framework.generics import ListAPIView, RetrieveAPIView

from areas.models import Area
from areas.serializers import AreaSerializer, SubAreaSerializer


class AreaProvinceView(ListAPIView):  # 查询所有的省份
    queryset = Area.objects.filter(parent=None)  # 所有的省份
    serializer_class = AreaSerializer
    pagination_class = None


class SubAreaView(RetrieveAPIView):  # 查询一个区域（城市和区县）
    queryset = Area.objects.all()
    serializer_class = SubAreaSerializer
