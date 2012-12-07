from django.conf.urls.defaults import patterns, include, url
from views import home, freudify

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^http://freudifier.herokuapp.com/$', home, name = 'slip_base_url'),
    url(r'^home', home, name = 'slip_home_url'),
    url(r'^freudify/(?P<url>.*)$', freudify, name = "slip_freudify_url")

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
