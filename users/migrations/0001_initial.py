# Generated by Django 3.1 on 2020-10-03 18:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('operators', '0001_initial'),
        ('places', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('screen_name', models.CharField(max_length=200, null=True)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default='M', max_length=15, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('safari_count', models.IntegerField(blank=True, default=0, null=True)),
                ('first_kudu_email', models.BooleanField(blank=True, default=False, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('luxury_level', models.CharField(choices=[('Luxury', 'Luxury'), ('Mid', 'Mid'), ('Back-to-basics', 'Back-to-basics')], max_length=20, null=True)),
                ('big_five', models.IntegerField(blank=True, default=0, null=True)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='images/user_avatar/%Y/%m/%d')),
                ('send_newsletter', models.BooleanField(default=False, null=True)),
                ('use_screen_name', models.BooleanField(blank=True, default=False, null=True)),
                ('hide_email', models.BooleanField(default=False, null=True)),
                ('withhold_information', models.BooleanField(default=False, null=True)),
                ('welcome_email_sent', models.BooleanField(default=False)),
                ('suppress_email', models.BooleanField(blank=True, default=False, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('website', models.CharField(blank=True, max_length=1000, null=True)),
                ('whatsapp', models.CharField(blank=True, max_length=1000, null=True)),
                ('blog', models.CharField(blank=True, max_length=1500, null=True)),
                ('skype', models.CharField(blank=True, max_length=1000, null=True)),
                ('linkedin', models.CharField(blank=True, max_length=1000, null=True)),
                ('facebook', models.CharField(blank=True, max_length=1000, null=True)),
                ('pinterest', models.CharField(blank=True, max_length=1000, null=True)),
                ('instagram', models.CharField(blank=True, max_length=1000, null=True)),
                ('youtube', models.CharField(blank=True, max_length=1000, null=True)),
                ('twitter', models.CharField(blank=True, max_length=1000, null=True)),
                ('user_type', models.CharField(choices=[('LO', 'Lodge staff/owner'), ('NP', 'Non-profit'), ('SG', 'Safari driver/guide'), ('SE', 'Safari enthusiast'), ('TO', 'Safari tour operator'), ('TA', 'Travel agency'), ('TW', 'Travel writer')], max_length=5, null=True)),
                ('reviews_count', models.IntegerField(default=0)),
                ('kudus_count', models.IntegerField(default=0)),
                ('activities_enjoy', models.ManyToManyField(blank=True, related_name='activities_enjoy', to='places.Activity')),
                ('animals_seen', models.ManyToManyField(blank=True, to='places.Animal')),
                ('badges', models.ManyToManyField(blank=True, to='users.Badge')),
                ('countries_visited', models.ManyToManyField(blank=True, related_name='countries_visited', to='places.CountryIndex')),
                ('country', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='places.country')),
                ('parks_visited', models.ManyToManyField(blank=True, related_name='parks_visited', to='places.Park')),
                ('tour_operator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='profiles', to='operators.touroperator')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Fav',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(blank=True, max_length=300, null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_deleted', models.DateTimeField(blank=True, null=True)),
                ('itinerary', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='favs', to='operators.itinerary')),
                ('tour_operator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='favs', to='operators.touroperator')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='favs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]