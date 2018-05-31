__author__ = 'Anthony'
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.conf import settings
from coversheets.models import Document
import csv
import sys
import os
from uuid import uuid4

# "Main"
class Command(BaseCommand):
    help = "Loads data from an excel spreadsheet and CSV into coversheets"

    def add_arguments(self, parser):
        parser.add_argument('filename',
                            type=str,
                            help='Path to csv document dump')
        parser.add_argument('maxload',
                            type=int,
                            help='Max number of documents to load. If None, loads all')

    def handle(self, filename, maxload=None, *args, **options):
        csv.field_size_limit(sys.maxsize)
        if filename is None:
            print self.usage()
            raise CommandError('No filename specified')
        load_count = 0
        with open(filename) as doc_dump:
            reader = csv.reader(doc_dump)
            for row in reader:
                try:
                    if maxload is not None and load_count > maxload:
                        break
                    outfiles_dir = settings.MEDIA_ROOT + "/documents/"
                    try:
                        outfile_name = row[4] + '.' + row[5]
                    except IndexError as e:
                        print row[:-1], e
                    outfile_path = outfiles_dir + outfile_name
                    if os.path.isfile(outfile_path):
                        outfile_name = str(uuid4()) + outfile_name
                        outfile_path = outfiles_dir + outfile_name
                    with File(open(outfile_path, 'wb')) as outfile:
                        try:
                            outfile.write(row[-1][2:].decode('hex'))
                        except TypeError as e:
                            print row[:-1], e
                            continue
                        outfile.flush()
                        try:
                            new_doc, created = Document.objects.get_or_create(description=row[3],
                                                                     file="/media/documents/" +outfile_name,
                                                                     jobsheet_id=row[-2],
                                                                     type=None,
                                                                     source=None)
                            load_count += 1
                        except ValueError as e:
                            print row[:-1], e
                except Exception as e:
                    print e, row[:-1], e