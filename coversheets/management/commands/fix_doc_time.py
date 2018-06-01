__author__ = 'Anthony'
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.conf import settings
from coversheets.models import Document
import csv
import sys
import os
from uuid import uuid4
from dateutil.parser import parse


# "Main"
class Command(BaseCommand):
    help = "Loads data from an excel spreadsheet and CSV into coversheets"

    def add_arguments(self, parser):
        parser.add_argument('filename',
                            type=str,
                            help='Path to csv document dump')

    def handle(self, filename, maxload=None, *args, **options):
        csv.field_size_limit(sys.maxsize)
        if filename is None:
            print self.usage()
            raise CommandError('No filename specified')
        update_count = 0
        with open(filename) as doc_dump:
            reader = csv.reader(doc_dump)
            for row in reader:
                try:
                    docs = Document.objects.filter(description=row[3],
                                               jobsheet_id=row[-2],
                                               type=None,
                                               source=None)

                    docs.update(created_at=parse(row[1]))
                    update_count += 1
                except Document.DoesNotExist:
                    print "Doc does not exist"
                except Document.MultipleObjectsReturned:
                    print "Multiple docs exist... sheet {}".format(row[-2])
                except Exception as e:
                    print e, row[:-1], e