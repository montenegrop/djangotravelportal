from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from operators.models import TourOperator
from users.models import UserProfile
import MySQLdb
from django.db.models import Count
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        # not allowed in production
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
        operators = TourOperator.objects.all()
        message = "tour_operator,user,last_seen\n"
        for operator in operators:
            profiles = UserProfile.objects.filter(
                tour_operator__id=operator.id)
            for profile in profiles:
                if profile.user.last_login:
                    last_login = profile.user.last_login
                else:
                    last_login = 'never'
                message_ = '"%s","%s","%s"'
                message_ = message_ % (
                    operator.name, profile.screen_name, last_login)
                message += message_ + "\n"
        self.stdout.write(self.style.SUCCESS(message))
