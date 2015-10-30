from django.conf.urls import patterns

urlpatterns = patterns(
    'tardis.apps.aus_synch_app',
    (r'^url-by-id/(?P<mongodb_id>\w+)/$', 'views.url_by_id'),
)

# import post_save hook on app init
from tardis.apps.aus_synch_app.hooks import *
