from rest_framework.response import Response
from rest_framework.views import APIView

from news.models import News, NewsCategory
from news.serializers import TopNewsSerializers, CategoryNewsSerializers


class NewsTopView(APIView):
    def get(self, request):
        # 获取新闻顶部列表
        slide_news = TopNewsSerializers(News.objects.filter(is_slide=True).exclude(img_url=''), many=True).data
        # 获取推荐新闻
        top_news = TopNewsSerializers(News.objects.order_by('-create_time')[0:10], many=True).data
        # 获取图片新闻
        image_news = TopNewsSerializers(News.objects.exclude(img_url='').order_by('-click')[0:4], many=True).data
        data = {
            "slide_news": slide_news,
            "top_news": top_news,
            "image_news": image_news,
        }
        return Response(data)


class NewsCategoryView(APIView):
    def get(self, request):
        # 查询所有的一级分类
        category_query = NewsCategory.objects.filter(parent_id=0)
        data_list = []
        for category in category_query:
            category_dict = CategoryNewsSerializers(category).data
            # 查询所有的二级分类
            s_category = category.newscategory_set.all()
            # 二级分类id列表
            id_list = []
            for cate in s_category:
                id_list.append(cate.id)
            # 分类新闻
            category_dict['news'] = TopNewsSerializers(
                News.objects.filter(category_id__in=id_list).exclude(img_url='').order_by(
                    '-create_time')[0:4], many=True).data
            # 新闻排行
            category_dict['top8'] = TopNewsSerializers(
                News.objects.filter(category_id__in=id_list).order_by(
                    '-click')[0:8], many=True).data
            data_list.append(category_dict)
        return Response(data_list)
