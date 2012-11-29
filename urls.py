from django.conf.urls.defaults import patterns, include, url
import settings
from local_conf import URL_PREFIX

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'slipper.views.home', name='home'),
    url(r'^%s' % URL_PREFIX, include('Slipper.slip.urls')),
    url(r'^%smedia/(?P<path>.*)$' % URL_PREFIX, 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}, name='stemweb_media_root_url')

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
