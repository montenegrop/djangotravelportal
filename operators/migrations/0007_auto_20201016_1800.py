# Generated by Django 3.1 on 2020-10-16 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operators', '0006_auto_20201016_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='touroperator',
            name='average_rating',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='touroperator',
            name='itinerary_quality',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='touroperator',
            name='meet_and_greet_rating',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='touroperator',
            name='responsiveness',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='touroperator',
            name='safari_quality',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='touroperator',
            name='vehicle_rating',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
