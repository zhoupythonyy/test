from django.conf.urls import url

from areas import views

urlpatterns = [
    url(r'^areas/$', views.AreaProvinceView.as_view()),
    url(r'^areas/(?P<pk>\d+)/$', views.SubAreaView.as_view()),
]