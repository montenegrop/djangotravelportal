from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from core.models import EmailLog
from django.core.files import File
import MySQLdb
from django.utils.timezone import make_aware


class Command(BaseCommand):
    help = 'Import animals'

    def add_arguments(self, parser):
        parser.add_argument('-db_host', required=True, type=str)
        parser.add_argument('-db_name', required=True, type=str)
        parser.add_argument('-db_user', required=True, type=str)
        parser.add_argument('-db_pass', required=True, type=str)

    def handle(self, *args, **options):
        # not allowed in production
        EmailLog.objects.all().delete()
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
        db = MySQLdb.connect(
            host=options['db_host'], db=options['db_name'], user=options['db_user'], password=options['db_pass'])
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        created, updated = 0, 0

        cursor.execute("select * from emaillog ORDER BY id DESC LIMIT 10000")
        result = cursor.fetchall()
        for c in result:
            newdict = {}
            
            newdict['address_to'] = c.pop('email_to')
            newdict['address_from'] = c.pop('email_from')
            newdict['subject'] = c.pop('email_subject')
            newdict['body'] = c.pop('email_body')
            newdict['cc'] = c.pop('email_cc')
            newdict['bcc'] = c.pop('email_bcc')
            
            newdict['date_created'] = make_aware(c['timestamp']) if c['timestamp'] else None
            newdict['date_opened'] = make_aware(c['opened']) if c['opened'] else None
            newdict['date_last_clicked'] = make_aware(c['last_checked']) if c['last_checked'] else None
            newdict['date_clicked'] = make_aware(c['clicked']) if c['clicked'] else None
            newdict['date_last_clicked'] = make_aware(c['last_clicked']) if c['last_clicked'] else None

            obj = EmailLog(**newdict)
            created += 1
            obj.save()
        message = 'Imported %i updated %i email logs' % (created, updated)

        self.stdout.write(self.style.SUCCESS(message))
