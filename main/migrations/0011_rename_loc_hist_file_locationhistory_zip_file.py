# Generated by Django 3.2 on 2021-05-20 02:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_locationhistory_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='locationhistory',
            old_name='loc_hist_file',
            new_name='zip_file',
        ),
    ]
