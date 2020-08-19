from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.validators import int_list_validator
from django.db import models, transaction
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from . import COMMENTS_ALLOW_HTML, get_user_display
from .managers import CommentManager


tree_path_validator = int_list_validator('/', 'Invalid comment tree path')


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
    object_pk = models.CharField(_('object ID'), max_length=64, db_index=True)
    content_object = GenericForeignKey(
        ct_field='content_type', fk_field='object_pk'
    )

    # Comment content
    body = models.TextField(_('comment'), db_column='comment')

    # Metadata about the comment
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    is_public = models.BooleanField(
        _('is public'), default=True, help_text=_(
            'Uncheck this box to make the comment '
            'effectively disappear from the site.'
        )
    )
    is_removed = models.BooleanField(
        _('is removed'), default=False, db_index=True, help_text=_(
            'Check this box if the comment is inappropriate. A "This '
            'comment has been removed" message will be displayed instead.'
        )
    )

    # Dates
    submit_date = models.DateTimeField(
        _('date/time submitted'), auto_now_add=True, db_index=True
    )
    edit_date = models.DateTimeField(
        _('date/time of last edit'), auto_now=True, db_index=True
    )

    class Meta:
        abstract = True

    @property
    def is_edited(self):
        """Check whether this comment has been edited."""
        return self.submit_date != self.edit_date

    @cached_property
    def _date(self):
        return self.submit_date.date()

    def get_content_object_url(self):
        """
        Get a URL suitable for redirecting to the content object.
        """
        return reverse(
            'comments-url-redirect',
            args=(self.content_type_id, self.object_pk)
        )

    def get_absolute_url(self, anchor_pattern='#c%(id)s'):
        return self.get_content_object_url() + (anchor_pattern % self.__dict__)


class AbstractTreeModel(models.Model):
    """An abstract model class representing a tree structure."""
    parent = models.ForeignKey(
        'self', related_name='replies', blank=True,
        null=True, on_delete=models.CASCADE
    )
    path = models.TextField(
        'tree path', editable=False, db_index=True,
        validators=(tree_path_validator,)
    )
    leaf = models.ForeignKey(
        'self', verbose_name='last child', blank=True,
        null=True, on_delete=models.SET_NULL
    )

    @property
    def _nodes(self):
        """Get the nodes of the path."""
        return self.path.split('/')

    @property
    def depth(self):
        """Get the depth of the tree."""
        return len(self._nodes)

    @property
    def root(self):
        """Get the id of the root node."""
        return int(self._nodes[0])

    @property
    def ancestors(self):
        """Get all nodes in the path excluding the last one."""
        return AbstractTreeModel.objects.filter(pk__in=self._nodes[:-1])

    class Meta:
        abstract = True
        ordering = ('path',)


class CommentAbstractModel(AbstractTreeModel, BaseCommentAbstractModel):
    """A user's comment about some object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='%(class)s_comments',
        verbose_name=_('user'), blank=True,
        null=True, on_delete=models.SET_NULL
    )

    # Manager
    objects = CommentManager()

    class Meta:
        abstract = True
        ordering = ('path', 'submit_date')
        permissions = (
            ('can_moderate', 'Can moderate comments'),
        )
        verbose_name = _('comment')
        verbose_name_plural = _('comments')

    def __str__(self):
        return '%s: %s...' % (self.user_display, strip_tags(self.body)[:50])

    @property
    def user_display(self):
        """Display the full name/username of the commenter."""
        return get_user_display(self.user)

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

    def is_editable_by(self, user):
        """Check if a comment can be edited or removed by a user."""
        return user == self.user

    @transaction.atomic
    def save(self, *args, **kwargs):
        super(CommentAbstractModel, self).save(*args, **kwargs)
        tree_path = str(self.id)
        if self.parent:
            tree_path = '%s/%s' % (self.parent.path, tree_path)
            self.parent.leaf = self
            CommentManager.filter(pk=self.parent_id).update(leaf=self.id)
        self.path = tree_path
        CommentManager.filter(id=self.id).update(path=self.path)

    def delete(self, *args, **kwargs):
        if self.parent_id:
            qs = CommentManager.filter(id=self.parent_id)
            qs.update(leaf=models.Subquery(
                qs.exclude(id=self.id).only('id')
                .order_by('-submit_date').values('id')[:1]
            ))
        super(CommentAbstractModel, self).delete(*args, **kwargs)
