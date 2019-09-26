from importlib import import_module

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.utils.module_loading import import_string


def _get_setting(setting, default):
    return getattr(settings, 'COMMENTS_' + setting, default)


COMMENTS_TIMEOUT = _get_setting('TIMEOUT', 360)  # 1h
COMMENTS_ALLOW_HTML = _get_setting('ALLOW_HTML', False)
COMMENTS_HIDE_REMOVED = _get_setting('HIDE_REMOVED', True)
COMMENTS_WIDGET = _get_setting('WIDGET', 'django.forms.Textarea')

if isinstance(COMMENTS_WIDGET, str):
    COMMENTS_WIDGET = import_string(COMMENTS_WIDGET)

DEFAULT_COMMENTS_APP = 'commentary'


def get_comment_app():
    """
    Get the comment app (i.e. "commentary") as defined in the settings
    """
    # Make sure the app's in INSTALLED_APPS
    comments_app = _get_setting('APP', DEFAULT_COMMENTS_APP)
    if not apps.is_installed(comments_app):
        raise ImproperlyConfigured(
            'The COMMENTS_APP (%r) must be in INSTALLED_APPS' % comments_app
        )
    # Try to import the package
    try:
        package = import_module(comments_app)
    except ImportError as e:
        raise ImproperlyConfigured(
            'The COMMENTS_APP setting refers '
            'to a non-existent package. (%s)' % e
        )

    return package


def _check_attr(attr):
    app = get_comment_app()
    return app.__name__ != DEFAULT_COMMENTS_APP and hasattr(app, attr)


def get_model():
    """
    Returns the comment model class.
    """
    if _check_attr('get_model'):
        return get_comment_app().get_model()
    else:
        from commentary.models import Comment
        return Comment


def get_form():
    from commentary.forms import CommentForm
    """
    Returns the comment ModelForm class.
    """
    if _check_attr('get_form'):
        return get_comment_app().get_form()
    else:
        return CommentForm


def get_form_target():
    """
    Returns the target URL for the comment form submission view.
    """
    if _check_attr('get_form_target'):
        return get_comment_app().get_form_target()
    else:
        return reverse('comments-post-comment')


def get_flag_url(comment):
    """
    Get the URL for the "flag this comment" view.
    """
    if _check_attr('get_flag_url'):
        return get_comment_app().get_flag_url(comment)
    else:
        return reverse('comments-flag', args=(comment.id,))


def get_delete_url(comment):
    """
    Get the URL for the "delete this comment" view.
    """
    if _check_attr('get_delete_url'):
        return get_comment_app().get_delete_url(comment)
    else:
        return reverse('comments-delete', args=(comment.id,))


def get_approve_url(comment):
    """
    Get the URL for the "approve this comment from moderation" view.
    """
    if _check_attr('get_approve_url'):
        return get_comment_app().get_approve_url(comment)
    else:
        return reverse('comments-approve', args=(comment.id,))


def get_user_display(user):
    """Get the full name or username to display for a user."""
    if _check_attr('get_user_display'):
        return get_comment_app().get_user_display(user)
    else:
        return user.get_full_name() or user.get_username()
