from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import get_user_display
from .abstracts import CommentAbstractModel


class Comment(CommentAbstractModel):
    class Meta(CommentAbstractModel.Meta):
        index_together = (
            ('content_type', 'object_pk')
        )


@python_2_unicode_compatible
class CommentFlag(models.Model):
    """
    Records a flag on a comment. This is intentionally flexible;
    right now, a flag could be:

        * A "removal suggestion" -- where a user suggests a comment
          for (potential) removal.

        * A "moderator deletion" -- used when a moderator deletes a comment.

    You can (ab)use this model to add other flags, if needed. However, by
    design users are only allowed to flag a comment with a given flag once;
    if you want rating look elsewhere.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('user'),
        related_name='comment_flags', on_delete=models.CASCADE,
    )
    comment = models.ForeignKey(
        # Translators: 'comment' is a noun here.
        Comment, verbose_name=_('comment'),
        related_name='flags', on_delete=models.CASCADE,
    )
    # Translators: 'flag' is a noun here.
    flag = models.CharField(_('flag'), max_length=30, db_index=True)
    flag_date = models.DateTimeField(_('date'), auto_now=True)

    # Constants for flag types
    SUGGEST_REMOVAL = 'removal suggestion'
    MODERATOR_DELETION = 'moderator deletion'
    MODERATOR_APPROVAL = 'moderator approval'

    class Meta:
        unique_together = (
            ('user', 'comment', 'flag'),
        )
        verbose_name = _('comment flag')
        verbose_name_plural = _('comment flags')

    def __str__(self):
        return '%s flag of comment ID %s by %s' % (
            self.flag, self.comment_id, get_user_display(self.user)
        )
