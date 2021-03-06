# Generated by Django 3.1 on 2020-10-03 18:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_to', models.CharField(max_length=2000)),
                ('address_from', models.CharField(max_length=2000)),
                ('subject', models.CharField(max_length=2000)),
                ('body', models.TextField()),
                ('cc', models.CharField(blank=True, max_length=2000, null=True)),
                ('bcc', models.CharField(blank=True, max_length=2000, null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_opened', models.DateTimeField(blank=True, null=True)),
                ('date_last_checked', models.DateTimeField(blank=True, null=True)),
                ('date_clicked', models.DateTimeField(blank=True, null=True)),
                ('date_last_clicked', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MissingInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('what_is_missing', models.CharField(choices=[('PARK', 'Park or game reserve'), ('OPERATOR', 'Tour Operator')], max_length=10)),
                ('name', models.CharField(max_length=400)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('how_did_you_hear', models.CharField(max_length=500)),
                ('description', models.CharField(max_length=2000)),
            ],
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/pages/%Y/%m/%d')),
                ('content', models.TextField()),
                ('meta_description', models.CharField(blank=True, max_length=1500, null=True)),
                ('meta_keywords', models.CharField(blank=True, max_length=700, null=True)),
                ('meta_title', models.CharField(blank=True, max_length=700, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MediaFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_modified', models.DateTimeField(auto_now=True, null=True)),
                ('image', models.ImageField(upload_to='images/mediafiles/%Y/%m/%d')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
