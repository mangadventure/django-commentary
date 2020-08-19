from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('commentary', '0004_commentary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='is_removed',
            field=models.BooleanField(
                db_index=True, default=False, help_text=(
                    'Check this box if the comment is inappropriate.'
                    ' A "This comment has been removed" message'
                    ' will be displayed instead.'
                ), verbose_name='is removed'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='object_pk',
            field=models.CharField(
                db_index=True, max_length=64, verbose_name='object ID'
            ),
        ),
        migrations.AlterUniqueTogether(
            name='commentflag',
            unique_together={('user', 'comment', 'flag')},
        ),
    ]
