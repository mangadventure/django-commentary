from django.core.exceptions import ImproperlyConfigured
from django.test.utils import modify_settings, override_settings

import commentary
from commentary.models import Comment
from commentary.forms import CommentForm

from . import CommentTestCase


class CommentAppAPITests(CommentTestCase):
    """Tests for the "comment app" API"""

    def testGetCommentApp(self):
        self.assertEqual(commentary.get_comment_app(), commentary)

    @modify_settings(INSTALLED_APPS={'remove': 'commentary'})
    def testGetMissingCommentApp(self):
        msg = "The COMMENTS_APP ('commentary') must be in INSTALLED_APPS"
        with self.assertRaisesMessage(ImproperlyConfigured, msg):
            commentary.get_comment_app()

    def testGetForm(self):
        self.assertEqual(commentary.get_form(), CommentForm)

    def testGetFormTarget(self):
        self.assertEqual(commentary.get_form_target(), "/post/")

    def testGetFlagURL(self):
        c = Comment(id=12345)
        self.assertEqual(commentary.get_flag_url(c), "/flag/12345/")

    def getGetDeleteURL(self):
        c = Comment(id=12345)
        self.assertEqual(commentary.get_delete_url(c), "/delete/12345/")

    def getGetApproveURL(self):
        c = Comment(id=12345)
        self.assertEqual(commentary.get_approve_url(c), "/approve/12345/")


@override_settings(
    COMMENTS_APP='custom_comments', ROOT_URLCONF='testapp.urls',
)
class CustomCommentTest(CommentTestCase):

    def testGetCommentApp(self):
        import custom_comments
        self.assertEqual(commentary.get_comment_app(), custom_comments)

    def testGetModel(self):
        from custom_comments.models import CustomComment
        self.assertEqual(commentary.get_model(), CustomComment)

    def testGetForm(self):
        from custom_comments.forms import CustomCommentForm
        self.assertEqual(commentary.get_form(), CustomCommentForm)

    def testGetFormTarget(self):
        self.assertEqual(commentary.get_form_target(), "/post/")

    def testGetFlagURL(self):
        c = Comment(id=12345)
        self.assertEqual(commentary.get_flag_url(c), "/flag/12345/")

    def getGetDeleteURL(self):
        c = Comment(id=12345)
        self.assertEqual(commentary.get_delete_url(c), "/delete/12345/")

    def getGetApproveURL(self):
        c = Comment(id=12345)
        self.assertEqual(commentary.get_approve_url(c), "/approve/12345/")
