# Generated by Django 3.1 on 2020-10-06 14:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0002_auto_20201005_2153'),
    ]

    operations = [
        migrations.RenameField(
            model_name='photo',
            old_name='uuid',
            new_name='uuid_value',
        ),
    ]