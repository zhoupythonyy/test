from rest_framework import serializers

from goods.models import Goods, GoodsCategory


class GoodsSerializers(serializers.ModelSerializer):
    """推荐商品序列化器"""
    class Meta:
        model = Goods
        fields = '__all__'


class SCategorySer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = ('id', 'title')


class CategorySer(serializers.ModelSerializer):
    goodscategory_set = SCategorySer(many=True, read_only=True)

    class Meta:
        model = GoodsCategory
        fields = ('id', 'title', 'goodscategory_set')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = '__all__'
