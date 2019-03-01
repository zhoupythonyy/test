from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from users import views

urlpatterns = [
    url(r'names/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
    url(r'register/$', views.UserView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),
]