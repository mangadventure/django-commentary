from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _, ngettext

from commentary import get_model
from commentary.views.moderation import (
    perform_flag, perform_approve, perform_delete
)

USERNAME_FIELD = 'user__' + get_user_model().USERNAME_FIELD


class CommentsAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'content_type', 'object_pk', 'parent',
        'submit_date', 'is_public', 'is_removed'
    )
    list_filter = (
        'submit_date', 'user', 'content_type',
        'is_public', 'is_removed'
    )
    date_hierarchy = 'submit_date'
    ordering = ('-submit_date',)
    raw_id_fields = ('user', 'parent')
    search_fields = ('body', USERNAME_FIELD)
    actions = ('flag_comments', 'approve_comments', 'remove_comments')

    def get_actions(self, request):
        actions = super(CommentsAdmin, self).get_actions(request)
        # Only superusers should be able to delete the comments from the DB.
        if not request.user.is_superuser:
            actions.pop('delete_selected', None)
        if not request.user.has_perm('commentary.can_moderate'):
            actions.pop('approve_comments', None)
            actions.pop('remove_comments', None)
        return actions

    def flag_comments(self, request, queryset):
        self._bulk_flag(
            request, queryset, perform_flag,
            lambda n: ngettext('flagged', 'flagged', n)
        )

    flag_comments.short_description = _('Flag selected comments')

    def approve_comments(self, request, queryset):
        self._bulk_flag(
            request, queryset, perform_approve,
            lambda n: ngettext('approved', 'approved', n)
        )

    approve_comments.short_description = _('Approve selected comments')

    def remove_comments(self, request, queryset):
        self._bulk_flag(
            request, queryset, perform_delete,
            lambda n: ngettext('removed', 'removed', n)
        )

    remove_comments.short_description = _('Remove selected comments')

    def _bulk_flag(self, request, queryset, action, done_message):
        """
        Flag, approve, or remove some comments from an admin action.
        Actually calls the `action` argument to perform the heavy lifting.
        """
        n_comments = 0
        for comment in queryset:
            action(request, comment)
            n_comments += 1
        msg = ngettext(
            '%(count)s comment was successfully %(action)s.',
            '%(count)s comments were successfully %(action)s.', n_comments
        )
        self.message_user(request, msg % {
            'count': n_comments, 'action': done_message(n_comments)
        })


# Only register the default admin if the model is the built-in comment model
# (this won't be true if there's a custom comment app).
Klass = get_model()
if Klass._meta.app_label == 'commentary':
    admin.site.register(Klass, CommentsAdmin)
