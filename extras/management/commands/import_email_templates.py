from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from post_office.models import EmailTemplate
from django.core.files import File
import MySQLdb
import os

class Command(BaseCommand):

    def handle(self, *args, **options):
        # not allowed in production
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
        path = 'extras/emails/'
        dir_list = os.listdir(path) 
        for f in dir_list:
            if f == '.' or f == '..':
                continue
            content = open(path+f).read()
            name = f[:-5]
            et,_ = EmailTemplate.objects.get_or_create(name=name)
            et.html_content = content
            et.save()
        total = 0
        message = 'Imported %i email templates' % total

        self.stdout.write(self.style.SUCCESS(message))
