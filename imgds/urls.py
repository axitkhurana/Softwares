from django.conf.urls.defaults import *

urlpatterns = patterns('imgds.views',
    url(r'^$','index'),
    url(r'^(?P<icategory>\w+)/$', 'browse', name='category'),
    url(r'^(?P<icategory>\w+)/(?P<isoftware>\w+)/$', 'browse', name='browse'),
    url(r'^search/', 'search', name='search'),
    url(r'^update/(?P<category>\w+)/$', 'pullfromfilehippo'),
    url(r'^update/(?P<category>\w+)/(?P<init>test)/$', 'pullfromfilehippo')
    )
