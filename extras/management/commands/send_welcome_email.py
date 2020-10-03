from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from users.models import UserProfile
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth

class Command(BaseCommand):
    help = ''

    def send_welcome_email(self, profile):
        email_to = profile.user.email
        if settings.DEBUG:
            email_to = settings.TESTING_EMAILS
        from post_office import mail
        link = settings.BASE_URL
        context = {'member': profile,
                    'link': link}
        mail.send(
            email_to,
            'Your African Safari <support@yourafricansafari.com>',
            template='facebook_registration',
            context=context,
        )
        profile.welcome_email_sent = True
        profile.save()

    def handle(self, *args, **options):
        associations = UserSocialAuth.objects.filter(user__profile__welcome_email_sent=False)
        count = 0
        for association in associations:
            self.send_welcome_email(association.user.profile)
            count += 1
        self.stdout.write(self.style.SUCCESS("SENT {}".format(count)))
