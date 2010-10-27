from django.conf.urls.defaults import *
from django.conf import settings
#from django.contrib.auth.views import login, logout

from home.views import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', index),
    (r'^admin/', include(admin.site.urls)),
    (r'^register/$', register),
    (r'^login/$', login),
    (r'^logout/$', logout),
    (r'^thanks/$', thanks),
    (r'^add/$', add_song),
    (r'^edit/(\d+)/$', edit_song),
    (r'^user/([\w.-]+)/$', view_user),
    (r'^song/(\d+)/$', view_song),
    (r'^scrape_ug/$', scrape_ug),
    (r'^delete/$', delete_song),
    (r'^top/artists/$', top_artists),
    (r'^artist/([\w ]+)/$', view_artist),
    (r'^tag/([\w ]+)/$', view_tag),
    (r'^explore/$', explore),
    (r'^about/$', about),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT},)
    )
