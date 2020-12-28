from time import time

from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.forms.utils import ErrorDict
from django.utils.crypto import salted_hmac, constant_time_compare
from django.utils.encoding import force_text
from django.utils.translation import gettext_lazy as _

from . import COMMENTS_TIMEOUT, COMMENTS_WIDGET, get_model


class CommentSecurityForm(forms.Form):
    """
    Handles the security aspects (anti-spoofing) for comment forms.
    """
    content_type = forms.CharField(widget=forms.HiddenInput)
    object_pk = forms.CharField(widget=forms.HiddenInput)
    timestamp = forms.IntegerField(widget=forms.HiddenInput)
    security_hash = forms.CharField(
        min_length=40, max_length=40, widget=forms.HiddenInput
    )
    honeypot = forms.CharField(
        required=False, label=_(
            'If you enter anything in this field '
            'your comment will be treated as spam'
        )
    )

    def __init__(self, target_object, data=None, initial=None, **kwargs):
        self.target_object = target_object
        if initial is None:
            initial = {}
        initial.update(self.generate_security_data())
        super(CommentSecurityForm, self).__init__(
            data=data, initial=initial, **kwargs
        )

    @property
    def security_errors(self):
        """Return just those errors associated with security"""
        errors = ('honeypot', 'timestamp', 'security_hash')
        return ErrorDict({
            f: self.errors[f] for f in errors if f in self.errors
        })

    def clean_honeypot(self):
        if self.cleaned_data['honeypot']:
            raise forms.ValidationError(self.fields['honeypot'].label)
        return ''

    def clean_security_hash(self):
        """Check the security hash."""
        expected_hash = self.generate_security_hash(
            self.data.get('content_type', ''),
            self.data.get('object_pk', ''),
            self.data.get('timestamp', '')
        )
        actual_hash = self.cleaned_data['security_hash']
        if not constant_time_compare(expected_hash, actual_hash):
            raise forms.ValidationError('Security hash check failed.')
        return actual_hash

    def clean_timestamp(self):
        """
        Make sure the timestamp isn't too far (default is 1 hour) in the past.
        """
        ts = self.cleaned_data['timestamp']
        if time() - ts > COMMENTS_TIMEOUT:
            raise forms.ValidationError('Timestamp check failed.')
        return ts

    def generate_security_data(self):
        """Generate a dict of security data for "initial" data."""
        timestamp = int(time())
        return {
            'content_type': str(self.target_object._meta),
            'object_pk': str(self.target_object._get_pk_val()),
            'timestamp': str(timestamp),
            'security_hash': self.initial_security_hash(timestamp)
        }

    def initial_security_hash(self, timestamp):
        """
        Generate the initial security hash from self.content_object
        and a (unix) timestamp.
        """
        return self.generate_security_hash(
            str(self.target_object._meta),
            str(self.target_object._get_pk_val()),
            str(timestamp)
        )

    def generate_security_hash(self, content_type, object_pk, timestamp):
        """
        Generate a HMAC security hash from the provided info.
        """
        info = '-'.join([content_type, object_pk, timestamp])
        key_salt = 'commentary.forms.CommentSecurityForm'
        return salted_hmac(key_salt, info).hexdigest()


class CommentForm(CommentSecurityForm):
    # Translators: 'Comment' is a noun here.
    comment = forms.CharField(
        label=_('Comment'), widget=COMMENTS_WIDGET
    )

    _model = get_model()

    def get_comment_object(self, site_id=settings.SITE_ID):
        if not self.is_valid():
            raise ValueError('Invalid form')
        return self._prevent_duplicates(self._model(
            content_type=ContentType.objects.get_for_model(self.target_object),
            object_pk=force_text(self.target_object._get_pk_val()),
            body=self.cleaned_data['comment'], site_id=site_id
        ))

    def _prevent_duplicates(self, new):
        comments = self._model.objects.filter(
            content_type=new.content_type, user=new.user,
            object_pk=new.object_pk, body=new.body
        )
        return next((c for c in comments if c._date == new._date), new)

    class Meta:
        fields = (
            'content_type', 'object_pk', 'timestamp',
            'security_hash', 'honeypot', 'comment'
        )
