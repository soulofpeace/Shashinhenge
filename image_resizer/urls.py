from django.conf.urls.defaults import *

urlpatterns = patterns('image_resizer.views',
    (r'^upload/$', 'upload'),
	(r'^(?P<image_id>\w+)/$',  'resize'),
    
)