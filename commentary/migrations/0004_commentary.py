# -*- coding: utf-8 -*-
import re

from django.core.validators import RegexValidator
from django.db import migrations, models
from django.db.models.functions import Cast


def set_comment_paths(apps, schema_editor):
    Comment = apps.get_model('commentary', 'Comment')
    pk = Cast('pk', models.TextField())
    Comment.objects.all().update(path=pk)


comment_path_validator = RegexValidator(
    re.compile(r'^\d+(?:/\d+)*\Z'), code='invalid',
    message='Invalid comment tree path'
)


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('commentary', '0003_add_submit_date_index'),
    ]

    operations = [
        migrations.AlterModelTable(name='comment', table=None),
        migrations.AlterModelTable(name='commentflag', table=None),
        migrations.AlterModelOptions(
            name='comment', options={
                'ordering': ('path', 'submit_date'),
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
        migrations.AddField(
            model_name='comment', name='leaf',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=models.deletion.SET_NULL,
                to='commentary.Comment', verbose_name='last child'
            ),
        ),
        migrations.AddField(
            model_name='comment', name='path',
            field=models.TextField(
                db_index=True, blank=True, default='', editable=False,
                validators=(comment_path_validator,), verbose_name='tree path',
            ),
        ),
        migrations.RunPython(set_comment_paths, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='comment', name='path',
            field=models.TextField(
                db_index=True, blank=False, editable=False,
                validators=(comment_path_validator,), verbose_name='tree path',
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
            model_name='commentflag', name='flag_date',
            field=models.DateTimeField(auto_now=True, verbose_name='date'),
        ),
    ]
