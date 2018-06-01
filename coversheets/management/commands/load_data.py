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
        "tblCallTypes": load_call_types,
        "ReferralTypes": load_referral_types,
        "tblLossTypes": load_loss_types,
        "tblAdjusters": load_adjusters,
        "tblInsuranceCompanies": load_insurance_companies,
        "tblStatusList": load_job_status,
        "tblEmployees": load_users,
    }
    create_groups()
    add_doc_types()
    add_sources()
    add_missing_cities()
    with open_workbook('coversheets_dump.xls') as wb:
        global BOOK_DATE_MODE
        BOOK_DATE_MODE = wb.datemode
        for sheet in wb.sheets():
            if sheet.name in sheet_map:
                sheet_map[sheet.name](sheet)
        load_job_sheets(wb.sheet_by_name("tblCoverSheetData"))
        load_job_numbers(wb.sheet_by_name("tblJobNumbers"))
        load_notes(wb.sheet_by_name("tblNotes"))

def load_basic_type(obj_type, sheet, kwargs):
    create_count = 0
    update_count = 0
    for row in range(sheet.nrows):
        if row == 0:
            continue
        row_kwargs = {keyword: sheet.cell(row, value).value for keyword, value in kwargs.iteritems()}
        obj, created = obj_type.objects.get_or_create(**row_kwargs)
        if created:
            create_count += 1
        else:
            update_count += 1
    print "created %d %s" % (create_count, str(obj_type))
    print "updated %d %s" % (update_count, str(obj_type))


def load_call_types(sheet):
    kwargs = {'id': 0,
              'type': 1
              }

    load_basic_type(ProgramType, sheet, kwargs)


def load_referral_types(sheet):
    kwargs = {'id': 0,
              'referral_type': 1,
              }
    load_basic_type(ReferralType, sheet, kwargs)


def load_insurance_companies(sheet):
    kwargs = {'id': 0,
              'name': 1,
              }
    load_basic_type(Insurance, sheet, kwargs)


def load_loss_types(sheet):
    kwargs = {'id': 0,
              'loss_type': 1,
              }
    load_basic_type(LossType, sheet, kwargs)


def load_job_status(sheet):
    kwargs = {'id': 0,
              'status': 1,
              }
    load_basic_type(JobStatus, sheet, kwargs)


def load_adjusters(sheet):
    """
    Adjusters require some special logic to handle phone number migration
    :param sheet:
    :return:
    """
    create_count, update_count = 0, 0
    for row in range(sheet.nrows):
        if row == 0:
            continue
        coversheet_id = sheet.cell(row, 0).value
        name = " ".join([sheet.cell(row, 1).value, sheet.cell(row, 2).value])
        phone = sheet.cell(row, 3).value  # "Phone"
        if phone == "":
            phone = sheet.cell(row, 5).value  # "Home Phone"
        fax = sheet.cell(row, 4).value
        if fax == "":
            fax = sheet.cell(row, 6).value  # "Home fax"
        mobile = sheet.cell(row, 7).value
        insurance_company_id = sheet.cell(row, 10).value
        if insurance_company_id == '':
            insurance_company_id = None
        email = sheet.cell(row, 11).value
        obj, created = Adjuster.objects.get_or_create(id=coversheet_id,
                                                      name=name,
                                                      phone=phone,
                                                      fax=fax,
                                                      mobile=mobile,
                                                      insurance_company_id=insurance_company_id,
                                                      email=email)
        if created:
            create_count += 1
        else:
            update_count += 1
    print "created %d %s" % (create_count, Adjuster)
    print "updated %d %s" % (update_count, Adjuster)


def load_users(sheet):
    create_count, update_count = 0, 0
    estimators_group = Group.objects.get(name="Estimators")
    supervisors_group = Group.objects.get(name="Superintendents")
    pm_group = Group.objects.get(name="Production Managers")
    coversheets_group = Group.objects.get(name="Coversheets")

    # Create "Unknown" user
    username = "unknown_user"
    email = "amlozano1@gmail.com"
    new_user, created = User.objects.get_or_create(username=username, email=email)
    new_user.first_name = "Unknown"
    new_user.save()
    global UNKNOWN_USER_ID
    UNKNOWN_USER_ID = new_user.id

    for row in range(sheet.nrows):
        if row == 0:
            continue
        user_id = sheet.cell(row, 0).value
        first_name = sheet.cell(row, 1).value
        last_name = sheet.cell(row, 2).value

        is_active = True if sheet.cell(row, 4).value == -1 else False
        is_staff = True

        username = sheet.cell(row, 11).value
        email = sheet.cell(row, 12).value
        if username == "":
            username = first_name + "." + last_name

        try:
            new_user, created = User.objects.get_or_create(id=user_id, username=username, email=email)
        except IntegrityError as e:
            print e
            print "User %s %s already exists!" % (first_name, last_name)
            continue
        new_user.set_password("Coversheets123")
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.is_active = is_active
        new_user.is_staff = is_staff
        new_user.save()
        coversheets_group.user_set.add(new_user)

        if sheet.cell(row, 3).value == -1:
            estimators_group.user_set.add(new_user)

        if sheet.cell(row, 5).value == -1:
            supervisors_group.user_set.add(new_user)

        if sheet.cell(row, 7).value == -1:
            pm_group.user_set.add(new_user)

        create_count += 1

    print "created %d %s" % (create_count, str(User))
    # print "updated %d %s" % (update_count, str(Users))


def load_job_numbers(sheet):
    for row in range(sheet.nrows):
        if row == 0:
            continue
        job_id = sheet.cell(row, 4).value
        job_nbr = sheet.cell(row, 1).value
        try:
            job = Job.objects.get(pk=job_id)
        except Job.DoesNotExist:
            print "Job number {} could not be loaded because jobsheet {} does not exist".format(job_nbr, job_id)
            continue
        job.add_job_number = True
        job.job_number = job_nbr
        job.save()


def load_notes(sheet):
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
            note, created = Note.objects.get_or_create(jobsheet_id=job_id, created_by_id=user_id, created_at=created_at,
                                       comment=comment)
            note.update(created_at=created_at)
        except Exception as e:
            print "Note on jobsheet {} failed to load because {}".format(job_id, e)


def load_documents(sheet):
    for row in range(sheet.nrows):
        if row == 0:
            continue


def load_job_sheets(sheet):
    create_count, update_count = 0, 0
    for row in range(sheet.nrows):
        if row == 0:
            continue
        try:
            kwargs = {}
            kwargs["id"] = int(sheet.cell(row, 0).value)

            kwargs["program_type_id"] = sheet.cell(row, 4).value
            kwargs["status_id"] = sheet.cell(row, 5).value
            kwargs["loss_type_id"] = sheet.cell(row, 6).value
            kwargs["called_in_by"] = sheet.cell(row, 7).value
            kwargs["referred_by"] = sheet.cell(row, 8).value
            kwargs["customer"] = sheet.cell(row, 9).value
            kwargs["primary_phone"] = sheet.cell(row, 11).value
            kwargs["mobile_phone"] = sheet.cell(row, 12).value
            kwargs["contact"] = sheet.cell(row, 14).value

            # kwargs["contact_email"]  = sheet.cell(row, 0).value

            # loss
            kwargs["loss_address"] = sheet.cell(row, 16).value
            kwargs["loss_city"] = sheet.cell(row, 17).value
            # kwargs["loss_state"] = sheet.cell(row, 18).value
            kwargs["loss_zip"] = sheet.cell(row, 19).value
            kwargs["directions"] = sheet.cell(row, 20).value

            # mailing
            kwargs["address"] = sheet.cell(row, 22).value
            kwargs["city"] = sheet.cell(row, 23).value
            kwargs["zip"] = sheet.cell(row, 25).value

            kwargs["adjuster_id"] = sheet.cell(row, 30).value
            kwargs["claim_number"] = sheet.cell(row, 37).value
            kwargs["policy_number"] = sheet.cell(row, 40).value
            kwargs["deductible"] = sheet.cell(row, 42).value
            kwargs["additional_info"] = sheet.cell(row, 45).value
            kwargs["emergency_requested"] = True if -1 == sheet.cell(row, 46).value else False
            kwargs["emergency_dispatch"] = sheet.cell(row, 48).value

            kwargs["estimator_id"] = sheet.cell(row, 52).value
            kwargs["info_taken_by_id"] = sheet.cell(row, 53).value
            kwargs["estimated_loss"] = sheet.cell(row, 54).value
            kwargs["production_manager_id"] = sheet.cell(row, 59).value
            kwargs["super_id"] = sheet.cell(row, 57).value
            # kwargs["status"] = sheet.cell(row, 0).value
            kwargs["referral_type_id"] = sheet.cell(row, 63).value

            kwargs["customer_email"] = sheet.cell(row, 76).value

            kwargs["insurance_company_id"] = sheet.cell(row, 28).value

            if kwargs['city'] != '':
                try:
                    city = City.objects.filter(name=fix_city(kwargs['city']))
                    kwargs['city_id'] = city[0].id
                except:
                    print kwargs['id'], 'Unknown Mailing City', repr(kwargs['city']), kwargs
                    continue
            del kwargs['city']
            if kwargs['loss_city'] != '':
                try:
                    loss_city = City.objects.filter(name=fix_city(kwargs['loss_city']))
                    kwargs['loss_city_id'] = loss_city[0].id
                    if 'city_id' not in kwargs:
                        kwargs['city_id'] = kwargs['loss_city_id']
                except:
                    print kwargs['id'], 'Unknown Loss City', repr(kwargs['loss_city'])
                    continue

            if kwargs['adjuster_id'] == '':
                del kwargs['adjuster_id']
            else:
                adj = Adjuster.objects.get(pk=int(kwargs['adjuster_id']))
                kwargs['insurance_company_id'] = adj.insurance_company_id

            if kwargs['info_taken_by_id'] == '':
                del kwargs['info_taken_by_id']
            else:
                try:
                    user = User.objects.get(pk=kwargs['info_taken_by_id'])
                except User.DoesNotExist:
                    kwargs['info_taken_by_id'] = UNKNOWN_USER_ID

            if kwargs['estimator_id'] == '':
                del kwargs['estimator_id']
            else:
                try:
                    user = User.objects.get(pk=kwargs['estimator_id'])
                except User.DoesNotExist:
                    kwargs['estimator_id'] = UNKNOWN_USER_ID

            if kwargs['super_id'] == '':
                del kwargs['super_id']
            else:
                try:
                    user = User.objects.get(pk=kwargs['super_id'])
                except User.DoesNotExist:
                    kwargs['super_id'] = UNKNOWN_USER_ID

            if kwargs['production_manager_id'] == '':
                del kwargs['production_manager_id']
            else:
                try:
                    user = User.objects.get(pk=kwargs['production_manager_id'])
                except User.DoesNotExist:
                    kwargs['production_manager_id'] = UNKNOWN_USER_ID

            if kwargs['referral_type_id'] == '':
                del kwargs['referral_type_id']
            if kwargs['insurance_company_id'] == '':
                del kwargs['insurance_company_id']
            del kwargs['loss_city']

            if kwargs['loss_type_id']:
                if not LossType.objects.filter(pk=int(kwargs['loss_type_id'])).exists():
                    print "jobsheet {} had an unknown loss type {}".format(kwargs['id'], kwargs['loss_type_id'])
                    kwargs['loss_type_id'] = 23

            if sheet.cell(row, 1).value == '':
                raise IntegrityError
            entry_date = xldate_as_tuple(sheet.cell(row, 1).value, BOOK_DATE_MODE)
            entry_time = xldate_as_tuple(sheet.cell(row, 2).value, BOOK_DATE_MODE)
            kwargs['entry_date'] = datetime(entry_date[0], entry_date[1], entry_date[2],
                                            entry_time[3], entry_time[4], entry_time[5], tzinfo=pytz.timezone("MST"))

            if sheet.cell(row, 36).value != '':
                datetuple = xldate_as_tuple(sheet.cell(row, 36).value, BOOK_DATE_MODE)
                claim_date = date(*datetuple[:3])
                kwargs["claim_date"] = claim_date

            kwargs2 = kwargs.copy()
            for keyword, arg in kwargs.iteritems():
                if arg == '':
                    del kwargs2[keyword]
            kwargs = kwargs2
            obj, created = Job.objects.get_or_create(**kwargs)

            if created:
                create_count += 1
            else:
                update_count += 1
        except IntegrityError as e:
            print kwargs['id'], ',', kwargs, e
            continue
        except TypeError as e:
            for key, value in kwargs.iteritems():
                print key, type(value)
            print kwargs
            raise
    print "created %d %s" % (create_count, Job)
    print "updated %d %s" % (update_count, Job)


def create_groups():
    app_label = 'coversheets'
    cities_label = 'cities_light'
    group, created = Group.objects.get_or_create(name='Coversheets')
    if created:
        # coversheets
        model_names = ['Job', 'Adjuster', 'Album', 'Image', 'Document', 'Note', 'Insurance']
        cts = ContentType.objects.filter(app_label=app_label, model=model_names)
        permissions = Permission.objects.filter(content_type=cts)
        for permission in permissions:
            group.permissions.add(permission)

        # cities_light
        model_names = ['city', 'country', 'region']
        cts = ContentType.objects.filter(app_label=cities_label, model=model_names)
        permissions = Permission.objects.filter(content_type=cts)
        for permission in permissions:
            group.permissions.add(permission)

    group, created = Group.objects.get_or_create(name='Management')
    if created:
        # coversheets
        cts = ContentType.objects.filter(app_label=app_label)  # All model_names
        permissions = Permission.objects.filter(content_type=cts)
        for permission in permissions:
            group.permissions.add(permission)

    group, created = Group.objects.get_or_create(name='Estimators')
    group, created = Group.objects.get_or_create(name='Superintendents')
    group, created = Group.objects.get_or_create(name='Production Managers')
    group, created = Group.objects.get_or_create(name='On Vacation')


def add_missing_cities():
    city = City
    region = Region
    country = Country
    arizona = region.objects.filter(name='Arizona')[0]
    usa = country.objects.get(code2='US')
    missing_az = [
        'Arizona City',
        'Awaktukee',
        'Carefree',
        'Cave Creek',
        'Coolidge',
        'Corvalis',
        'Forest Lakes',
        'Gold Canyon',
        'Higley',
        'Laveen',
        'Litchfield Park',
        'New River',
        'Palo Verde',
        'Paradise Valley',
        'Pinal County',
        'Queen Valley',
        'Rio Verde',
        'Sacaton',
        'Sedona',
        'Springerville',
        'Show Low',
        'Sun Lakes',
        'Tolleson',
        'Tonopah',
        'Waddell',
        'Wickenburg',
        'Wikieup',
        'Wittmann',
        'Youngtown',
    ]
    objs = [city.objects.get_or_create(name=name, region=arizona, country=usa)[0] for name in missing_az]

    city.objects.get_or_create(name='Saddle Brook', region=region.objects.get(name="New Jersey"), country=usa)
    city.objects.get_or_create(name='Corry', region=region.objects.get(geoname_code="PA"), country=usa)
    city.objects.get_or_create(name='San Marino', region=region.objects.get(geoname_code="CA"), country=usa)
    city.objects.get_or_create(name='Ozone Park', region=region.objects.get(geoname_code="NY"), country=usa)
    city.objects.get_or_create(name='Wayzata', region=region.objects.get(geoname_code="MN"), country=usa)


def fix_city(city):
    city = city.strip()
    lowered = city.lower()
    if lowered in ['phoenix', 'phoenix', 'pheonix', 'awahtukee', 'phoeniz', 'phoeinx', 'phoenx', 'phoenix,']:
        return 'Phoenix'
    elif lowered in ['mesa']:
        return 'Mesa'
    elif lowered in ['apache jot', 'apache jct', 'apachie junction']:
        return 'Apache Junction'
    elif lowered in ['litchfield', 'litchfiled park', 'licthfield park']:
        return 'Litchfield Park'
    elif lowered in ['las henderson']:
        return 'Henderson'
    elif lowered in [' scottsdale', 'scottsdale', 'scottdsdale', 'scottdale']:
        return 'Scottsdale'
    elif lowered in ['gold cayon']:
        return 'Gold Canyon'
    elif lowered in ['sun city']:
        return 'Sun City'
    elif lowered in ['forest lakes estates', 'forest lakes estates']:
        return 'Forest Lakes'
    elif lowered in ['chander', 'chandler']:
        return 'Chandler'
    elif lowered in ['buckeye']:
        return 'Buckeye'
    elif lowered in ['surrprise', 'surprise']:
        return 'Surprise'
    elif lowered in ['peoria']:
        return 'Peoria'
    elif lowered in ['fountain hills']:
        return 'Fountain Hills'
    elif lowered in ['paradise valley', 'paradisse valley']:
        return 'Paradise Valley'
    elif lowered in ['toungtown']:
        return 'Youngtown'
    elif lowered in ['goodyear']:
        return 'Goodyear'
    elif lowered in ['gilbert']:
        return 'Gilbert'
    elif lowered in ['coolidge']:
        return 'Coolidge'
    elif lowered in ['queencreek']:
        return "Queen Creek"
    elif lowered in ['laveen village', 'lavene']:
        return 'Laveen'
    elif lowered in ['tempe']:
        return 'Tempe'
    elif lowered in ['ft. wayne']:
        return 'Fort Wayne'
    elif lowered in ['calgary, alberta, canada']:
        return 'Calgary'
    elif lowered in ['vancover']:
        return 'Vancouver'
    elif lowered in ['Arleta']:
        return 'Los Angeles'
    elif lowered in ['']:
        return ''
    elif lowered in ['']:
        return ''
    elif lowered in ['']:
        return ''
    else:
        return city


def add_sources():
    sources = """A All Rite Floor Covering Inc
A Shade Above
AAA Emergency Tree Service, LLC
ABP Electrical
Absolut Restoration
Acuity Builders & Construction, Inc.
Advanced Garage Solutions & More LLC
All Pro Fence
All Service Plumbing
AllCoat Surfacing Technologies
Allen Environmental Services
Arizona Hardwood Floor Supply Inc
Arizona Strategic Enterprises
Armed Electric
AZ Premier Services LLC
Banker Insulation
Bell Drapery Cleaners
Better Drywall LLC
C & C Painting And Drywall
Cardinal Clean LLC
Carports Etc
Cave's Canopies and Steel Inc
Completely Wired LLC
CTB Construction, Inc.
Custom Fence & Gates Inc.
Don Witt Engineering Associates
Dynamic Concrete
Eagle Flooring West
Eco Clean
Elite Valley Contents
Emergency Cleanup LLC
Fireplace Southwest
Flooring Network
Floors Unlimited, Inc.
Free Plastering, Inc.
Friedhoff Consulting Services
FRSTeam by Butlers
G & C Glass Inc.
Gilbert Structural
Good Guys Drywall
Greystroke Custom Painting
Hayden Lane, LLC
Hewitt Material
IDT Landscaping, LLC
Inca Roofing, Inc.
Invision Electric
Jackpot Sanitation Services
Jess Delph - Prime Design
JM Homes
Lodi Garage Doors and More
Marble Colors Restoration Inc.
Master Contents Services
Mesa Fully Formed
Metro Fire Equipment, Inc.
MJM Masonry INC
Modern Stairs and Railings
MorningStar Homes LLC
Moser's Valley View Glass
Nationwide Shower Doors
Natural Stone Care
Neff Enterprises, Inc.
Neil S Storage Cabinets
Next Step Floors, LLC
Northrop Development
Precision Restoration LLC
Quality Aire
Quality Stucco Corp ACC
RAD Fire Protection, Inc
Ram Wallcoverings
Riggs & Ellsworth Electric Inc.
Romualdo's Stucco
Ryse Construction
Scottsdale AllCoat Surfacing Technologies
Shade Tree Mechanical
Sierra Waste Systems
Skinner Interiors Systems, Inc.
Starling Madison Lofquist, Inc.
Stealth Demolition
Stonehenge
Summit Roofing
Sundance Industries
Taurus Moving, LLC
TCS Northern Division Ltd
Tempe Dzign Center
Thistle Door LLC
Thomson Mechanical, Inc.
Trek Cleaning
True View
Valley Pro Electric
Valleywide Awnings, Inc.
Viking Specialty Services LLC
Wat-A-Blast
Western Garage Doors, Inc.
Wheeler Air Conditioning
"""
    for source in sources.splitlines():
        DocumentSource.objects.get_or_create(name=source)


def add_doc_types():
    types = ['Invoice', 'Bid', 'Permit', 'Receipts', 'Reports']
    for some_type in types:
        DocumentType.objects.get_or_create(type=some_type)


# def gh():
# import csv
#     import sys
#     csv.field_size_limit(sys.maxsize)
#     with open(r"C:\Users\Anthony\Desktop\2.csv") as csvfile:
#         reader = csv.reader(csvfile)
#         rows = list(reader)
#     return rows
#
# def wh(rows):
#     with open(r"C:\Users\Anthony\Desktop\test.pdf", 'wb') as pdf:
#         pdf.write(rows[0][-1].decode('hex'))


# "Main"
class Command(NoArgsCommand):

    help = "Loads data from an excel spreadsheet and CSV into coversheets"

    option_list = NoArgsCommand.option_list + (
        make_option('--verbose', action='store_true'),
    )

    def handle_noargs(self, **options):
        load_all()


