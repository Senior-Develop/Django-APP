# Generated by Django 3.2 on 2021-05-27 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20210527_0029'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='locationhistory',
            name='session',
        ),
        migrations.AddField(
            model_name='locationhistory',
            name='session_key',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
