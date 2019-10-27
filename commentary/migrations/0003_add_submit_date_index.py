# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commentary', '0002_update_user_email_field_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='submit_date',
            field=models.DateTimeField(
                default=None, db_index=True,
                verbose_name='date/time submitted'
            ),
            preserve_default=True,
        ),
    ]
