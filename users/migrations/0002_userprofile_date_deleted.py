# Generated by Django 3.1 on 2020-10-14 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='date_deleted',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
