from django.conf.urls.defaults import *

urlpatterns = patterns('imgds.views',
    (r'^update/(?P<category>\w+)/$', 'pullfromfilehippo'),
#    (r'^update/(?P<category>\w+)/init/$, '
    )
