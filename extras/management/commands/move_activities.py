from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from places.models import Activity
from operators.models import ItineraryActivity
from django.template.defaultfilters import slugify

class Command(BaseCommand):
    help = 'Move activities'

    def handle(self, *args, **options):
        # not allowed in production
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
            return False
        for ia in ItineraryActivity.objects.all():
            try:
                ac = Activity.objects.get(name=ia.name)
            except Activity.DoesNotExist:
                try:
                    ac = Activity.objects.get(name_short=ia.name_short)
                except Activity.DoesNotExist:
                    ac = False
            if not ac:
                print(ia,'not found')
                ac = Activity()
                ac.name_old = 'non-existent'
            else:
                ac.name_old = ac.name
            ac.name = ia.name
            ac.name_short = ia.name_short
            ac.activity_level = ia.activity_level
            ac.description = ia.description
            ac.slug = slugify(ia.name)
            ac.save()
            ac.focus_type.set(ia.focus_type.all())
            
        message = 'Moved activities' 

        self.stdout.write(self.style.SUCCESS(message))
