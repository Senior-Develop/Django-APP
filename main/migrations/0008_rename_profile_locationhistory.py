# Generated by Django 3.2 on 2021-05-14 23:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_alter_profile_loc_hist_file'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Profile',
            new_name='LocationHistory',
        ),
    ]
