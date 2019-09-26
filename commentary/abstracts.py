from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from . import COMMENTS_ALLOW_HTML, get_user_display
from .managers import CommentManager


class BaseCommentAbstractModel(models.Model):
    """
    An abstract base class that any custom comment models probably should
    subclass.
    """
    # Content-object field
    content_type = models.ForeignKey(
        ContentType, verbose_name=_('content type'),
        related_name='content_type_set_for_%(class)s', on_delete=models.CASCADE
    )
    object_pk = models.CharField(_('object ID'), max_length=255)
    content_object = GenericForeignKey(
        ct_field='content_type', fk_field='object_pk'
    )

    # Metadata about the comment
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def get_content_object_url(self):
        """
        Get a URL suitable for redirecting to the content object.
        """
        return reverse(
            'comments-url-redirect',
            args=(self.content_type_id, self.object_pk)
        )


@python_2_unicode_compatible
class CommentAbstractModel(BaseCommentAbstractModel):
    """
    A user comment about some object.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='%(class)s_comments',
        verbose_name=_('user'), blank=True,
        null=True, on_delete=models.SET_NULL
    )

    body = models.TextField(_('comment'), db_column='comment')

    submit_date = models.DateTimeField(
        _('date/time submitted'), auto_now_add=True, db_index=True
    )
    edit_date = models.DateTimeField(
        _('date/time of last edit'), auto_now=True, db_index=True
    )

    is_public = models.BooleanField(
        _('is public'), default=True, help_text=_(
            'Uncheck this box to make the comment '
            'effectively disappear from the site.'
        )
    )
    is_removed = models.BooleanField(
        _('is removed'), default=False, help_text=_(
            'Check this box if the comment is inappropriate. A "This '
            'comment has been removed" message will be displayed instead.'
        )
    )

    parent = models.ForeignKey(
        'self', related_name='replies', blank=True,
        null=True, on_delete=models.CASCADE
    )

    # TODO: add upvotes & downvotes

    # Manager
    objects = CommentManager()

    class Meta:
        abstract = True
        ordering = ('submit_date',)
        permissions = (
            ('can_moderate', 'Can moderate comments'),
        )
        verbose_name = _('comment')
        verbose_name_plural = _('comments')

    def __str__(self):
        return '%s: %s...' % (self.user_display, strip_tags(self.body)[:50])

    @property
    def is_edited(self):
        """Check whether this comment has been edited."""
        return self.submit_date != self.edit_date

    @property
    def user_display(self):
        """Display the full name/username of the commenter."""
        return get_user_display(self.user)

    @cached_property
    def _date(self):
        return self.submit_date.date()

    def get_absolute_url(self, anchor_pattern='#c%(id)s'):
        return self.get_content_object_url() + (anchor_pattern % self.__dict__)

    def strip_body(self):
        return strip_tags(self.body) if COMMENTS_ALLOW_HTML else self.body

    def get_as_text(self):
        """
        Return this comment as plain text. Useful for emails.
        """
        return _(
            'Posted by %(user)s at %(date)s\n\n'
            '%(comment)s\n\nhttp://%(domain)s%(url)s'
        ) % {
            'user': self.user_display,
            'date': self.submit_date,
            'comment': self.strip_body(),
            'domain': self.site.domain,
            'url': self.get_absolute_url()
        }
