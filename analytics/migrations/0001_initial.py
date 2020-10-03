# Generated by Django 3.1 on 2020-10-03 18:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Analytic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(blank=True, choices=[('VISIT', 'Visit'), ('CLICK', 'Click')], db_index=True, max_length=15, null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('ip_address', models.CharField(max_length=300)),
                ('device_type', models.CharField(max_length=300)),
                ('browser_type', models.CharField(max_length=300)),
                ('browser_version', models.CharField(max_length=300)),
                ('os_type', models.CharField(max_length=300)),
                ('os_version', models.CharField(max_length=300)),
                ('referer', models.TextField(blank=True, null=True)),
                ('path', models.CharField(blank=True, max_length=350, null=True)),
                ('country_short', models.CharField(blank=True, max_length=20, null=True)),
                ('page_url', models.URLField(blank=True, null=True)),
                ('object_id', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('F', 'Favorite'), ('K', 'Kudu'), ('L', 'Like'), ('U', 'Up Vote'), ('D', 'Down Vote'), ('H', 'Helpful')], db_index=True, max_length=1)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('object_id', models.PositiveIntegerField(blank=True, db_index=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='contenttypes.contenttype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
