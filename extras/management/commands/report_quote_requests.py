from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from operators.models import QuoteRequest, TourOperator, Itinerary, ItineraryExtra, ItineraryType
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
        message = "tour_operator,quote_date\n"
        for operator in operators:
            quotes = QuoteRequest.objects.filter(
                tour_operator__id=operator.id).filter(date_created__year=2019)
            for quote in quotes:
                message_ = '"%s","%s"'
                message_ = message_ % (
                    operator.name, quote.date_created,)
                message += message_ + "\n"
        self.stdout.write(self.style.SUCCESS(message))
