# Generated by Django 3.1 on 2020-10-03 18:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Itinerary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images/itineraries/%Y/%m/%d')),
                ('title', models.CharField(max_length=300)),
                ('title_short', models.CharField(blank=True, max_length=300, null=True)),
                ('slug', models.SlugField(max_length=255)),
                ('header', models.TextField(blank=True, null=True)),
                ('needs_update', models.BooleanField(default=True)),
                ('summary', models.TextField(blank=True, null=True)),
                ('content', models.TextField()),
                ('accomodation', models.TextField(blank=True, null=True)),
                ('min_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('max_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('search_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('single_supplement', models.BooleanField(default=False)),
                ('accept_terms', models.BooleanField(default=False)),
                ('single_supplement_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('duration', models.CharField(blank=True, max_length=300, null=True)),
                ('days', models.IntegerField(blank=True, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18)], null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('flight', models.BooleanField(default=False)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_deleted', models.DateTimeField(blank=True, null=True)),
                ('other_inclusion', models.BooleanField(default=False)),
                ('other_inclusion_text', models.CharField(blank=True, max_length=300, null=True)),
                ('other_exclusion', models.BooleanField(default=False)),
                ('other_exclusion_text', models.CharField(blank=True, max_length=300, null=True)),
                ('activity_level', models.IntegerField(default=0)),
                ('activity_level_name', models.CharField(blank=True, default='', max_length=300, null=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('visit_count', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Itineraries',
            },
        ),
        migrations.CreateModel(
            name='ItineraryActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('name_short', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True, null=True)),
                ('activity_level', models.IntegerField()),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Itinerary activities',
            },
        ),
        migrations.CreateModel(
            name='ItineraryDayDescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_number', models.IntegerField()),
                ('title', models.CharField(max_length=300)),
                ('description', models.CharField(max_length=5000)),
                ('lodging', models.CharField(blank=True, max_length=300, null=True)),
                ('date_deleted', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ItineraryExclusion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('explanation', models.CharField(blank=True, max_length=400, null=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ItineraryFocusType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='ItineraryInclusion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('explanation', models.CharField(blank=True, max_length=400, null=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ItineraryType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Itinerary types',
            },
        ),
        migrations.CreateModel(
            name='Month',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('name_short', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('show_contact_information', models.BooleanField(default=False)),
                ('show_contact_form', models.BooleanField(default=False)),
                ('show_logo', models.BooleanField(default=False)),
                ('show_gallery', models.BooleanField(default=False)),
                ('show_social_network', models.BooleanField(default=False)),
                ('show_itinerary', models.BooleanField(default=False)),
                ('max_description', models.IntegerField(default=0)),
                ('max_vehicle_description', models.IntegerField(default=0)),
                ('max_photo', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='QuoteRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=600)),
                ('email', models.EmailField(max_length=254)),
                ('date_trip', models.DateField()),
                ('days', models.IntegerField()),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_modified', models.DateTimeField(blank=True, null=True)),
                ('date_deleted', models.DateTimeField(blank=True, null=True)),
                ('telephone', models.CharField(blank=True, max_length=300, null=True)),
                ('party_size', models.CharField(max_length=300)),
                ('additional_information', models.TextField()),
                ('follow_up_email_sent', models.BooleanField(default=False)),
                ('ip_address', models.CharField(blank=True, max_length=300, null=True)),
                ('status', models.CharField(choices=[('QA', 'QA'), ('PENDING', 'Pending'), ('SEEN', 'Seen')], default='QA', max_length=15)),
                ('seen', models.BooleanField(default=False)),
                ('seen_on', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TourOperator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('luxury_level', models.CharField(choices=[('BUDGET', 'Budget'), ('MID_LEVEL', 'Mid-range'), ('ULTRA_SAFARI', 'Luxury')], default='MID_LEVEL', max_length=25)),
                ('name', models.CharField(max_length=300, verbose_name='Company name')),
                ('name_short', models.CharField(blank=True, max_length=300, null=True)),
                ('slug', models.SlugField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('vehicle_description', models.TextField(blank=True, null=True)),
                ('projects', models.CharField(blank=True, max_length=300, null=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='images/touroperators_logo/%Y/%m/%d')),
                ('startup_date', models.DateField(blank=True, null=True)),
                ('last_seen', models.DateTimeField(blank=True, null=True)),
                ('last_reviewed', models.DateField(blank=True, null=True)),
                ('tailored_safari', models.BooleanField(default=True)),
                ('book_attraction', models.BooleanField(default=True)),
                ('international_flight', models.BooleanField(default=True)),
                ('group_safari', models.BooleanField(default=True)),
                ('contact', models.CharField(blank=True, max_length=300, null=True, verbose_name='Contact name')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('secondary_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('telephone', models.CharField(blank=True, max_length=300, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('validated', models.BooleanField(default=True)),
                ('date_deleted', models.DateTimeField(blank=True, null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('first_kudu_email', models.BooleanField(blank=True, default=False, null=True)),
                ('not_trading', models.BooleanField(default=False)),
                ('out_of_business', models.BooleanField(default=False)),
                ('yas_modifier', models.IntegerField(default=0)),
                ('suppress_email', models.BooleanField(default=False)),
                ('widget_added', models.BooleanField(default=False)),
                ('draft', models.BooleanField(default=False)),
                ('website', models.CharField(blank=True, max_length=1000, null=True)),
                ('whatsapp', models.CharField(blank=True, max_length=1000, null=True)),
                ('blog', models.CharField(blank=True, max_length=1000, null=True)),
                ('skype', models.CharField(blank=True, max_length=1000, null=True)),
                ('linkedin', models.CharField(blank=True, max_length=1000, null=True)),
                ('facebook', models.CharField(blank=True, max_length=1000, null=True)),
                ('pinterest', models.CharField(blank=True, max_length=1000, null=True)),
                ('instagram', models.CharField(blank=True, max_length=1000, null=True)),
                ('youtube', models.CharField(blank=True, max_length=1000, null=True)),
                ('twitter', models.CharField(blank=True, max_length=1000, null=True)),
                ('yas_score', models.IntegerField(default=0)),
                ('date_modified_yas_score', models.DateTimeField(blank=True, null=True)),
                ('reviews_count', models.IntegerField(blank=True, null=True)),
                ('average_rating', models.IntegerField(blank=True, null=True)),
                ('packages_count', models.IntegerField(blank=True, null=True)),
                ('quote_request_count', models.IntegerField(blank=True, null=True)),
                ('parks_count', models.IntegerField(blank=True, null=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('last_review_date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='YASScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yas_score', models.IntegerField(default=0)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
