from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.decorators.cache import cache_page

from .views import home
from .views import info
from .views import sql

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^info/(?P<db>[0-9a-zA-Z_]+)/(?P<table>[0-9a-zA-Z_ -]+)/$',
        info, name='info-columns'),
    url(r'^info/(?P<db>[0-9a-zA-Z_]+)/$', info, name='info-tables'),
    url(r'^info/$', info, name='info'),
    url(r'^sql/(?P<db>[0-9a-zA-Z_]+)/$', cache_page(5*60)(sql), name='sql'),
    url(r'^$', home, name='home'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
