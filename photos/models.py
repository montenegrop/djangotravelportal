from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from operators.models import TourOperator, Itinerary
from places.models import Activity, CountryIndex, Park
from reviews.models import KilimanjaroParkReview, ParkReview, TourOperatorReview
from django.utils import timezone
from users.models import UserProfile
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.template import defaultfilters
from analytics.models import Action, Analytic
from yas import settings
from post_office.models import EmailTemplate
from django.template import Template, Context
from post_office import mail


class Tag(models.Model):
    name = models.CharField(max_length=1000)

    def __str__(self):
        return self.name


class Photo(models.Model):
    image = models.ImageField(upload_to='images/photos/%Y/%m/%d')
    caption = models.CharField(max_length=1500, blank=True, null=True)
    uuid_value = models.CharField(max_length=100)
    tags = models.ManyToManyField(Tag, blank=True)
    animals = models.ManyToManyField('places.Animal', blank=True)
    tour_operator = models.ForeignKey(
        TourOperator, on_delete=models.PROTECT, blank=True, null=True, related_name='photos')
    itinerary = models.ForeignKey(Itinerary, on_delete=models.PROTECT, blank=True, null=True, related_name='photos')
    itinerary_cover = models.BooleanField(default=False)
    country_index = models.ForeignKey(
        CountryIndex, on_delete=models.PROTECT, blank=True, null=True, related_name='photos')
    park = models.ForeignKey(
        Park, on_delete=models.PROTECT, blank=True, null=True, related_name='photos')
    activity = models.ForeignKey(
        Activity, on_delete=models.PROTECT, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True)
    date_deleted = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True)
    draft = models.BooleanField(default=False)
    actions = GenericRelation(Action, related_query_name='photo')
    kudu_count = models.IntegerField(default=0)
    park_review = models.ForeignKey(
        ParkReview, on_delete=models.PROTECT, blank=True, null=True, related_name='photos')
    tour_operator_review = models.ForeignKey(
        TourOperatorReview, on_delete=models.CASCADE, blank=True, null=True, related_name='photos')
    visit_count = models.IntegerField(default=0)

    def check_and_send_kudu_email(self):
        if self.user and self.user.profile.suppress_email:
            return
        if self.tour_operator and self.tour_operator.suppress_email:
            return

        if self.kudu_count == 1 or self.kudu_count == 25 or self.kudu_count == 50 or self.kudu_count == 1000:
            if self.user and self.user.profile.first_kudu_email and self.kudu_count == 1:
                return
            if self.tour_operator and self.tour_operator.first_kudu_email and self.kudu_count == 1:
                return
            if self.user:
                email_string = self.user.first_name + " " + \
                    self.user.last_name + "<" + self.user.email + ">"

            if self.tour_operator:
                email_string = ", ".join(
                    self.tour_operator.email_recipient_list())

            if self.kudu_count == 1 and self.tour_operator:
                self.tour_operator.first_kudu_email = True
                self.tour_operator.save()

            if self.kudu_count == 1 and self.user:
                self.user.profile.first_kudu_email = True
                self.user.profile.save()

            if self.kudu_count == 1:
                subject = "Congratulations on your first kudu!"
                template = EmailTemplate.objects.get(name="single_kudu_email")
            else:
                subject = "%d people have given your photo a kudu" % self.kudu_count
                template = EmailTemplate.objects.get(name="kudu_email")

            t = Template(template.html_content)
            c = Context({'photo': self, 'base_url': settings.BASE_URL})
            mail_body = t.render(c)
            """
            log_entry = EmailLog()
            log_entry.address_to = email_string
            log_entry.address_from  = 'YAS Support <yas@yourafricansafari.com>'
            log_entry.subject = subject
            log_entry.body = mail_body
            log_entry.save()
            c = Context({'photo': self, 'base_url': settings.BASE_URL, 'emaillog_id' : log_entry.pk })
            """
            # mail.send(
            #    email_string,
            #    'YAS Support <yas@yourafricansafari.com>',
            #    subject=subject,
            #    html_message=t.render(c),
            # )

    def update_kudu_count(self):
        self.kudu_count = Action.objects.filter(action_type='K').filter(
            content_type__model='photo').filter(photo=self).count()
        self.save()

    def caption_slugged(self):
        if self.caption:
            return defaultfilters.slugify(self.caption)
        else:
            return ""

    def get_caption_excerpt(self):
        if self.caption and len(self.caption) > 75:
            return self.caption[:75] + '...'
        return self.caption or ""

    def get_description(self):
        result = "Photo "
        if self.taken_at():
            result += " taken at <i>%s</i>" % self.taken_at()
        if self.user:
            if not self.taken_at():
                result += " taken "
            result += " by <i>%s</i>" % self.user.profile.__str__()
        if self.tour_operator:
            result += " by tour operator <i>%s</i>" % self.tour_operator.name
        return result

    def taken_at(self):
        if self.park and self.country_index:
            return "%s, %s" % (self.park.__str__(), self.country_index.__str__())
        if self.park:
            return self.park.__str__()
        if self.country_index:
            return self.country_index.__str__()

    def is_tagged(self):
        return self.animals.count() or self.country_index or self.park or self.activity or self.tags.count()

    def save(self,*args, **kwargs):
        import uuid
        self.uuid = uuid.uuid4()
        super(Photo, self).save(*args, **kwargs)


    class Meta:
        ordering = ['-id']


class Comment(models.Model):
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey()
    date_created = models.DateTimeField(default=timezone.now)
    STATUS_PENDING = 'PENDING'
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_CHOICES = (
        (STATUS_PENDING, "Draft"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "rejected"),)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default=STATUS_ACCEPTED)
