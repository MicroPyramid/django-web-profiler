from django.conf.urls import url
from .views import (index, records_list, device_records_list)

app_name = 'django_web_profiler'

urlpatterns = [
    # url(r'^home/$','home'),
    url(r'^$', index, name="index"),
    url(r'^records/list/(?P<record_id>[-\w]+)/$', records_list, name='records_list'),

    url(r'^device-records-list/$', device_records_list, name='device_records_list'),

]
