from django.conf.urls.defaults import patterns, include, url
from views import home, freudify
from local_conf import URL_PREFIX

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'slipper.views.home', name='home'),
    url(r'^%shome' % URL_PREFIX, home, name = 'slip_home_url'),
    url(r'^%sfreudify/(?P<url>.*)$' % URL_PREFIX, freudify, name = "slip_freudify_url")

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
