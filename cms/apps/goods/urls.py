from django.conf.urls import url

from goods import views

urlpatterns = [
    url(r'goods/recommend/$', views.RecommendView.as_view()),
    url(r'goods/categories/$', views.CategoriesView.as_view()),
    url(r'goods/category/$', views.GoodsListView.as_view()),
    url(r'goods/category/(?P<pk>\d+)/$', views.CategoryView.as_view()),
]