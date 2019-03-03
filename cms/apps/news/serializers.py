from rest_framework.serializers import ModelSerializer

from news.models import News, NewsCategory


class TopNewsSerializers(ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'


class SNewsSerializers(ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = ('id', 'title')


class CategoryNewsSerializers(ModelSerializer):
    newscategory_set = SNewsSerializers(many=True, read_only=True)

    class Meta:
        model = NewsCategory
        fields = ('id', 'title', 'newscategory_set')
