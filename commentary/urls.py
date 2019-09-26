from django.conf.urls import url
from django.contrib.contenttypes.views import shortcut

from .views.comments import post_comment
from .views.moderation import flag, delete, approve


urlpatterns = [
    url(r'^post/$', post_comment, name='comments-post-comment'),
    url(r'^flag/(\d+)/$', flag, name='comments-flag'),
    url(r'^delete/(\d+)/$', delete, name='comments-delete'),
    url(r'^approve/(\d+)/$', approve, name='comments-approve'),
    url(r'^cr/(\d+)/(.+)/$', shortcut, name='comments-url-redirect'),
]
