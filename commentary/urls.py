from django.contrib.contenttypes.views import shortcut
from django.urls import path, re_path

from .views.comments import post_comment
from .views.moderation import flag, delete, approve


urlpatterns = [
    path('post/', post_comment, name='comments-post-comment'),
    path('flag/<int:comment_id>/', flag, name='comments-flag'),
    path('delete/<int:comment_id>/', delete, name='comments-delete'),
    path('approve/<int:comment_id>/', approve, name='comments-approve'),
    re_path(r'^cr/(\d+)/(.+)/$', shortcut, name='comments-url-redirect'),
]
