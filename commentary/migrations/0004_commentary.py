# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('commentary', '0003_add_submit_date_index'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={
                'ordering': ('submit_date',),
                'permissions': (
                    ('can_moderate', 'Can moderate comments'),
                ),
                'verbose_name': 'comment', 'verbose_name_plural': 'comments'
            },
        ),
        migrations.RenameField(
            model_name='comment', old_name='comment', new_name='body'
        ),
        migrations.AlterField(
            model_name='comment', name='body',
            field=models.TextField(db_column='comment', verbose_name='comment'),
        ),
        migrations.AlterField(
            model_name='comment', name='object_pk',
            field=models.CharField(max_length=255, verbose_name='object ID'),
        ),
        migrations.AlterField(
            model_name='comment', name='submit_date',
            field=models.DateTimeField(
                auto_now_add=True, db_index=True,
                verbose_name='date/time submitted'
            ),
        ),
        migrations.AddField(
            model_name='comment', name='edit_date',
            field=models.DateTimeField(
                auto_now=True, db_index=True,
                verbose_name='date/time of last edit'
            ),
        ),
        migrations.AddField(
            model_name='comment', name='parent',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=models.deletion.CASCADE,
                related_name='replies', to='commentary.Comment'
            ),
        ),
        migrations.RemoveField(model_name='comment', name='ip_address'),
        migrations.RemoveField(model_name='comment', name='user_email'),
        migrations.RemoveField(model_name='comment', name='user_name'),
        migrations.RemoveField(model_name='comment', name='user_url'),
        migrations.AlterIndexTogether(
            name='comment', index_together={('content_type', 'object_pk')},
        ),
        migrations.AlterField(
            model_name='commentflag',
            name='flag_date',
            field=models.DateTimeField(auto_now=True, verbose_name='date'),
        ),
    ]
