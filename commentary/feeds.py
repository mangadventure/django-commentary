from django.contrib.sites.shortcuts import get_current_site
from django.contrib.syndication.views import Feed
from django.utils.translation import gettext as _

from . import get_model


class LatestCommentFeed(Feed):
    """Feed of latest comments on the current site."""
    def __call__(self, request, *args, **kwargs):
        self.site = get_current_site(request)
        return super(LatestCommentFeed, self).__call__(
            request, *args, **kwargs
        )

    @property
    def title(self):
        return _('%(site_name)s comments') % {
            'site_name': self.site.name
        }

    @property
    def description(self):
        return _('Latest comments on %(site_name)s') % {
            'site_name': self.site.name
        }

    @property
    def items(self):
        return get_model().objects.filter(
            site__pk=self.site.pk,
            is_public=True,
            is_removed=False,
        ).order_by('-submit_date')[:40]

    def item_pubdate(self, item):
        return item.submit_date

    def item_updateddate(self, item):
        return item.edit_date

    def item_author_name(self, item):
        return item.user_display
