# Generated by Django 3.1 on 2020-10-13 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='countryindex',
            name='header_class',
            field=models.CharField(blank=True, max_length=400),
        ),
        migrations.AddField(
            model_name='park',
            name='header_class',
            field=models.CharField(blank=True, max_length=400),
        ),
    ]
