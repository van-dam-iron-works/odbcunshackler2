from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.decorators.cache import cache_page

from .views import home
from .views import info
from .views import sql

admin.autodiscover()

urlpatterns = patterns('',
    url(ur'^info/(?P<db>[a-zA-Z_]+)/$', info, name='info'),
    url(ur'^sql/(?P<db>[a-zA-Z_]+)/$', cache_page(5*60)(sql), name='sql'),
    url(ur'^$', home, name='home'),
    url(ur'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(ur'^admin/', include(admin.site.urls)),
)
