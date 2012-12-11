from django.conf.urls.defaults import patterns, include, url
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^media/(?P<path>.*)$', 'django.views.static.serve',\
		{'document_root': settings.MEDIA_ROOT}, name='freudifier_media_root_url'),
    url(r'^', include('freudifier.slip.urls'))
   

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
