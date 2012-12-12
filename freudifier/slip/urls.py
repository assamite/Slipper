from django.conf.urls.defaults import patterns, include, url
from views import home, freudify, what

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', home, name = 'slip_base_url'),
    url(r'^what/$', what, name = 'slip_what_url'),
    url(r'^contribute/$', home, name = 'slip_contribute_url'),
    url(r'^(?P<url>.*)$', freudify, name = "slip_freudify_url")

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
