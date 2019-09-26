=================
Django Commentary
=================

.. image:: https://img.shields.io/pypi/v/django-commentary.svg?label=PyPI&logo=pypi
   :target: https://pypi.python.org/pypi/django-commentary
   :alt: PyPI

.. image:: https://img.shields.io/travis/mangadventure/django-commentary?label=Travis&logo=travis
   :target: https://travis-ci.org/mangadventure/django-commentary
   :alt: Travis CI

This is a fork of `django-contrib-comments`__ with the following changes:

* |c| Only users can post comments.
* |c| Previews have been removed.
* |c| Posting a comment redirects to the comment page.
* |u| Post/flag/approve/delete redirect back to the page.
* |u| Users can edit and delete their own comments.
* |u| Comments are threaded.

This framework can be used to attach comments to any model, so you can use it
for comments on blog entries, photos, book chapters, or anything else.

For details, `consult the documentation`__.

__ https://github.com/django/django-contrib-comments
__ https://django-commentary.readthedocs.io

.. |u| unicode:: U+2610
.. |c| unicode:: U+2611
