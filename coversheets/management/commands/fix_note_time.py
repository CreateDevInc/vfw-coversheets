# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import IntegrityError, transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, User, Permission
from django.core.management.base import NoArgsCommand, make_option
from cities_light.models import City, Country, Region
from coversheets.models import DocumentSource, DocumentType, Adjuster, Note, ReferralType, ProgramType, Insurance, \
    LossType, JobStatus, Job
from xlrd import open_workbook, xldate_as_tuple
from datetime import datetime, date
import pytz

BOOK_DATE_MODE = None
UNKNOWN_USER_ID = -1

@transaction.atomic
def load_all():
    """
    Make sure to arrange the excel spreadsheet so that employees are loaded first and jobs are loaded last.
    :return:
    """
    sheet_map = {
    }
    with open_workbook('coversheets_dump.xls') as wb:
        global BOOK_DATE_MODE
        BOOK_DATE_MODE = wb.datemode
        for sheet in wb.sheets():
            if sheet.name in sheet_map:
                sheet_map[sheet.name](sheet)
        fix_notes(wb.sheet_by_name("tblNotes"))


def fix_notes(sheet):
    for row in range(sheet.nrows):
        if row == 0:
            continue
        job_id = int(sheet.cell(row, 3).value)
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist as e:
            "Note on jobsheet {} failed to load because {}".format(job_id, e)
            continue
        user_id = sheet.cell(row, 2).value
        if user_id == "":
            user_id = UNKNOWN_USER_ID
        else:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                user_id = UNKNOWN_USER_ID

        entry_date = xldate_as_tuple(sheet.cell(row, 4).value, BOOK_DATE_MODE)
        # entry_time = xldate_as_tuple(sheet.cell(row, 5).value, BOOK_DATE_MODE)
        created_at = datetime(entry_date[0], entry_date[1], entry_date[2],
                              entry_date[3], entry_date[4], entry_date[5], tzinfo=pytz.timezone("MST"))
        comment = sheet.cell(row, 6).value
        try:
            notes = Note.objects.filter(jobsheet_id=job_id, created_by_id=user_id, comment=comment)
            if notes is not None and len(notes) == 1:
                notes.update(created_at=created_at)
            elif notes is not None:
                print "Note could not be updated, non-unique %s" % notes
            else:
                continue
        except Exception as e:
            print "Note on jobsheet {} failed to load because {}".format(job_id, e)

class Command(NoArgsCommand):

    help = "Loads data from an excel spreadsheet and CSV into coversheets"

    option_list = NoArgsCommand.option_list + (
        make_option('--verbose', action='store_true'),
    )

    def handle_noargs(self, **options):
        load_all()


