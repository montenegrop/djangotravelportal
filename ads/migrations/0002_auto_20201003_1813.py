# Generated by Django 3.1 on 2020-10-03 18:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('places', '0001_initial'),
        ('operators', '0002_auto_20201003_1813'),
        ('ads', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='country_indexes',
            field=models.ManyToManyField(blank=True, to='places.CountryIndex'),
        ),
        migrations.AddField(
            model_name='ad',
            name='itinerary',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='operators.itinerary'),
        ),
    ]
