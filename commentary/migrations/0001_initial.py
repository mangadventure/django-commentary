# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True
                )),
                ('object_pk', models.TextField(verbose_name='object ID')),
                ('user_name', models.CharField(
                    max_length=50, blank=True, verbose_name="user's name"
                )),
                ('user_email', models.EmailField(
                    max_length=75, blank=True,
                    verbose_name="user's email address"
                )),
                ('user_url', models.URLField(
                    verbose_name="user's URL", blank=True
                )),
                ('comment', models.TextField(
                    max_length=3000, verbose_name='comment'
                )),
                ('submit_date', models.DateTimeField(
                    default=None, verbose_name='date/time submitted'
                )),
                ('ip_address', models.GenericIPAddressField(
                    unpack_ipv4=True, null=True,
                    verbose_name='IP address', blank=True
                )),
                ('is_public', models.BooleanField(
                    default=True, verbose_name='is public',
                    help_text='Uncheck this box to make the comment'
                              ' effectively disappear from the site.',
                )),
                ('is_removed', models.BooleanField(
                    default=False, verbose_name='is removed',
                    help_text='Check this box if the comment is inappropriate.'
                              ' A "This comment has been removed" message'
                              ' will be displayed instead.'
                )),
                ('content_type', models.ForeignKey(
                    related_name='content_type_set_for_comment',
                    verbose_name='content type', to='contenttypes.ContentType',
                    on_delete=models.CASCADE
                )),
                ('site', models.ForeignKey(
                    to='sites.Site', on_delete=models.CASCADE
                )),
                ('user', models.ForeignKey(
                    related_name='comment_comments', verbose_name='user',
                    blank=True, to=settings.AUTH_USER_MODEL,
                    null=True, on_delete=models.SET_NULL
                )),
            ],
            options={
                'ordering': ('submit_date',),
                'db_table': 'django_comments',
                'verbose_name': 'comment',
                'verbose_name_plural': 'comments',
                'permissions': [('can_moderate', 'Can moderate comments')],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CommentFlag',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True
                )),
                ('flag', models.CharField(
                    max_length=30, verbose_name='flag', db_index=True
                )),
                ('flag_date', models.DateTimeField(
                    default=None, verbose_name='date'
                )),
                ('comment', models.ForeignKey(
                    related_name='flags', verbose_name='comment',
                    to='commentary.Comment', on_delete=models.CASCADE
                )),
                ('user', models.ForeignKey(
                    related_name='comment_flags', verbose_name='user',
                    to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                )),
            ],
            options={
                'db_table': 'django_comment_flags',
                'verbose_name': 'comment flag',
                'verbose_name_plural': 'comment flags',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='commentflag',
            unique_together={'user', 'comment', 'flag'},
        ),
    ]
