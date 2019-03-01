from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from goods import serializers
from goods.models import Goods, GoodsCategory


class RecommendView(ListAPIView):
    """获取推荐商品"""
    queryset = Goods.objects.filter(is_red=1).order_by('-create_time')[0:4]
    serializer_class = serializers.GoodsSerializers


class CategoriesView(APIView):
    """分类商品"""
    def get(self, request):
        # 获取所有的大分类
        cate_query = GoodsCategory.objects.filter(parent_id=0)
        data_list = []
        for cate in cate_query:
            cate_dict = serializers.CategorySer(cate).data
            # 获取小分类
            s_cate = cate.goodscategory_set.all()
            id_list = []
            for i in s_cate:
                id_list.append(i.id)
            cate_dict['goods'] = serializers.GoodsSerializers(Goods.objects.filter(category_id__in=id_list).order_by('-create_time')[0:5], many=True).data
            data_list.append(cate_dict)
        return Response(data_list)


class GoodsListView(ListAPIView):
    """查询商品列表数据"""
    serializer_class = serializers.GoodsSerializers
    queryset = Goods.objects.filter(status=0)

    # 配置排序和过滤的管理类
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('create_time', 'sell_price', 'sales')	   # 排序字段
    filter_fields = ('category', )  # 过滤字段


class CategoryView(GenericAPIView):
    """面包屑导航"""
    queryset = GoodsCategory.objects.all()

    def get(self, request, pk=None):
        cate = self.get_object()
        if cate.parent_id == 0:
            # 当前类别为一级类别
            s_category = cate.goodscategory_set.all()
            id_list = []
            for i in s_category:
                id_list.append(i.id)
            goods_list = serializers.GoodsSerializers(Goods.objects.filter(category_id__in=id_list), many=True).data
            category = serializers.CategorySerializer(cate).data
            category['parent'] = 'null'

            category['goods_list'] = goods_list

        else:
            category = serializers.CategorySerializer(cate).data
            category['parent'] = serializers.CategorySerializer(cate.parent).data
        return Response(category)