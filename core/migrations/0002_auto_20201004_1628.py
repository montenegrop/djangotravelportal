# Generated by Django 3.1 on 2020-10-04 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediafile',
            name='alt_text',
            field=models.CharField(default='', max_length=1500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mediafile',
            name='slug',
            field=models.SlugField(default='', unique=True),
            preserve_default=False,
        ),
    ]
