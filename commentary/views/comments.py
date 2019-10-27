from __future__ import absolute_import

from django import http
from django.apps import apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.messages import error
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.html import escape
from django.views.decorators.cache import patch_cache_control
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from commentary import get_form, get_user_display, signals


class CommentPostBadRequest(http.HttpResponseBadRequest):
    """
    Response returned when a comment post is invalid. If ``DEBUG`` is on a
    nice-ish error message will be displayed (for debugging purposes), but in
    production mode a simple opaque 400 page will be displayed.
    """
    def __init__(self, why):
        super(CommentPostBadRequest, self).__init__()
        if settings.DEBUG:
            self.content = render_to_string(
                'comments/400-debug.html', {'why': why}
            )


@csrf_protect
@require_POST
@login_required
def post_comment(request, next=None, using=None):
    """Post a comment. HTTP POST is required."""
    # Look up the object we're trying to comment about
    ctype = request.POST.get('content_type')
    object_pk = request.POST.get('object_pk')
    if ctype is None or object_pk is None:
        return CommentPostBadRequest('Missing content_type or object_pk field.')
    try:
        model = apps.get_model(*ctype.split('.', 1))
        target = model._default_manager.using(using).get(pk=object_pk)
    except TypeError:
        return CommentPostBadRequest(
            'Invalid content_type value: %r' % escape(ctype)
        )
    except AttributeError:
        return CommentPostBadRequest(
            'The given content-type %r does not '
            'resolve to a valid model.' % escape(ctype)
        )
    except ObjectDoesNotExist:
        return CommentPostBadRequest(
            'No object matching content-type %r and '
            'object PK %r exists.' % (
                escape(ctype), escape(object_pk)
            )
        )
    except (ValueError, ValidationError) as e:
        return CommentPostBadRequest(
            'Attempting to get content-type %r '
            'and object PK %r raised %s' % (
                escape(ctype), escape(object_pk), e.__class__.__name__
            )
        )

    # Construct the comment form
    form = get_form()(target, data=request.POST)

    # Check security information
    if form.security_errors:
        return CommentPostBadRequest(
            'The comment form failed security verification: %s' % escape(
                str(form.security_errors)
            )
        )

    if form.errors:
        for err in form.errors:
            error(request, err, 'comment')
        return http.HttpResponseRedirect(target.get_absolute_url())

    # Create the comment
    comment = form.get_comment_object(site_id=get_current_site(request).id)
    comment.user = request.user

    # Signal that the comment is about to be saved
    responses = signals.comment_will_be_posted.send(
        sender=comment.__class__,
        comment=comment,
        request=request
    )

    for receiver, response in responses:
        if response is False:
            return CommentPostBadRequest(
                'comment_will_be_posted receiver %r '
                'killed the comment' % receiver.__name__
            )

    # Save the comment and signal that it was saved
    comment.save()
    signals.comment_was_posted.send(
        sender=comment.__class__,
        comment=comment,
        request=request
    )

    return http.HttpResponseRedirect(comment.get_absolute_url())
