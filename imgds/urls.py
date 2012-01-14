from django.conf.urls.defaults import *

urlpatterns = patterns('imgds.views',
    (r'^update/$', 'pullfromfilehippo'),
    )
