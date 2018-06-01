from datetime import timedelta, datetime, time
from django.db import models
from django.contrib.auth.models import User
from django.views.generic.list import ListView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from forms import AlbumUpload, Report, EmailObjs
from models import Image, Job, Adjuster, JobStatus, User, Insurance, LossType, ProgramType, ReferralType, Document
from itertools import groupby
from pytz import timezone

# Create your views here.

def home(request):
    return HttpResponse("Hello world")

@login_required()
def show_album(request, album):
    context = {}
    context['images'] = Image.objects.filter(album=album)
    return render(request, "show_album.html", context)

@login_required()
def add_album(request):
    if request.method == 'POST' and request.POST:
        form = AlbumUpload(request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
        #     album = Album(form['cleaned_data'].album_name)
        #     album.save()
        #     images = [Image(image_file=file, album=album, uploaded_by=request.user) for file in file_list]
        #     for image in images:
        #         image.save()
        return render(request, "multi_upload_template.html", {'form': form})
    else:
        return render(request, "multi_upload_template.html", {'form': AlbumUpload()})


def by_entry_date(request, start, end, show_empty, show_most_recent_note, statuses):
    midnight = time(tzinfo=timezone('US/Arizona'))
    tables = []
    one_day = timedelta(days=1)
    datetimes = [datetime.combine(start + timedelta(days=days), midnight) for days in range((end-start).days)]
    sections = []
    for start_datetime in datetimes:
        tables = []
        for status in statuses:
            table = {'status': status}
            end_datetime = start_datetime + one_day
            jobs_of_the_day = Job.objects.filter(entry_date__gt=start_datetime,
                                                 entry_date__lt=end_datetime,
                                                 status=status).select_related('estimator',
                                                                               'super',
                                                                               'insurance_company',
                                                                               'adjuster',
                                                                               'status',
                                                                               'loss_type',
                                                                               'program_type',
                                                                               'referral_type')
            table['jobs'] = jobs_of_the_day
            table.update(jobs_of_the_day.aggregate(count=models.Count('pk'),
                                                   sum=models.Sum('estimated_loss'),
                                                   avg=models.Avg('estimated_loss'),
                                                   min=models.Min('estimated_loss'),
                                                   max=models.Max('estimated_loss')))
            if not show_empty and table['count'] == 0:
                continue
            else:
                tables.append(table)
        # outer loop
        total_jobs = Job.objects.filter(entry_date__gt=start_datetime,
                                        entry_date__lt=end_datetime,
                                        status__in=statuses).aggregate(count=models.Count('pk'),
                                                                               sum=models.Sum('estimated_loss'),
                                                                               avg=models.Avg('estimated_loss'),
                                                                               min=models.Min('estimated_loss'),
                                                                               max=models.Max('estimated_loss'))
        section = {'title': start_datetime.strftime("%b %d, %Y"), 'tables': tables}
        section.update(total_jobs)
        if not show_empty and section['count'] == 0:
            continue
        sections.append(section)
    return render(request, "job_list.html", {'sections': sections,
                                             'start': start,
                                             'end': end,
                                             'obj_type': 'Date',
                                             'show_most_recent_note': show_most_recent_note})


def by_fk(request, start, end, show_empty, show_most_recent_note, statuses, obj_type, type_name_field, job_field):
    job_list = Job.objects.filter(entry_date__gt=start,
                                  entry_date__lt=end,
                                  status__in=statuses).select_related('estimator',
                                                                      'super',
                                                                      'insurance_company',
                                                                      'adjuster',
                                                                      'status',
                                                                      'loss_type',
                                                                      'program_type',
                                                                      'referral_type')
    if show_empty:
        objects = obj_type.objects.all()
    else:
        objects = obj_type.objects.filter(job__id__in=job_list).distinct()
    type_name = obj_type._meta.verbose_name.title()
    sections = []
    for obj in objects:
        tables = []
        for status in statuses:
            table = {'status': status}
            filter_kwargs = {job_field: obj, 'status': status}
            jobs = job_list.filter(**filter_kwargs)
            table['jobs'] = jobs
            table.update(jobs.aggregate(count=models.Count('pk'),
                                        sum=models.Sum('estimated_loss'),
                                        avg=models.Avg('estimated_loss'),
                                        min=models.Min('estimated_loss'),
                                        max=models.Max('estimated_loss')))
            if not show_empty and table['count'] == 0:
                continue
            tables.append(table)
        filter_kwargs = {job_field: obj, 'status__in': statuses}
        total_jobs = job_list.filter(**filter_kwargs).aggregate(count=models.Count('pk'),
                                                                sum=models.Sum('estimated_loss'),
                                                                avg=models.Avg('estimated_loss'),
                                                                min=models.Min('estimated_loss'),
                                                                max=models.Max('estimated_loss'))
        section = {'title': getattr(obj, type_name_field), 'tables': tables}
        section.update(total_jobs)
        if not show_empty and section['count'] == 0:
            continue
        sections.append(section)

    return render(request, "job_list.html", {'job_list': job_list,
                                             'sections': sections,
                                             'start': start,
                                             'end': end,
                                             'obj_type': type_name,
                                             'show_most_recent_note': show_most_recent_note})

def by_user_group(request, start, end, show_empty, show_most_recent_note, statuses, group_name, job_field, related_name):
    job_list = Job.objects.filter(entry_date__gt=start,
                                  entry_date__lt=end,
                                  status__in=statuses).select_related('estimator',
                                                                      'super',
                                                                      'insurance_company',
                                                                      'adjuster',
                                                                      'status',
                                                                      'loss_type',
                                                                      'program_type',
                                                                      'referral_type',
                                                                      'most_recent_note')
    if show_empty:
        objects = User.objects.filter(groups__name=group_name, is_active=True)
    else:
        keyword = related_name + "__id__in"
        filter_kwargs = {keyword: job_list, 'groups__name': group_name, 'is_active': True}
        objects = User.objects.filter(**filter_kwargs).distinct()
    sections = []
    for obj in objects:
        tables = []
        for status in statuses:
            table = {'title': obj.first_name + ' ' + obj.last_name,
                     'status': status}
            filter_kwargs = {job_field: obj, 'status': status}
            jobs = job_list.filter(**filter_kwargs)
            table['jobs'] = jobs
            table.update(jobs.aggregate(count=models.Count('pk'),
                                        sum=models.Sum('estimated_loss'),
                                        avg=models.Avg('estimated_loss'),
                                        min=models.Min('estimated_loss'),
                                        max=models.Max('estimated_loss')))
            if not show_empty and table['count'] == 0:
                continue
            tables.append(table)
        # outer loop
        filter_kwargs = {job_field: obj, 'status__in': statuses}
        total_jobs = job_list.filter(**filter_kwargs).aggregate(count=models.Count('pk'),
                                                                sum=models.Sum('estimated_loss'),
                                                                avg=models.Avg('estimated_loss'),
                                                                min=models.Min('estimated_loss'),
                                                                max=models.Max('estimated_loss'))
        section = {'title': obj.first_name + ' ' + obj.last_name, 'tables': tables}
        section.update(total_jobs)
        if not show_empty and section['count'] == 0:
            continue
        sections.append(section)
    return render(request, "job_list.html", {'job_list': job_list,
                                             'sections': sections,
                                             'start': start,
                                             'end': end,
                                             'obj_type': group_name,
                                             'show_most_recent_note': show_most_recent_note})


@login_required()
def reports(request):
    if request.method == 'POST' and request.POST:
        form = Report(request.POST)
        if form.is_valid():
            if form.cleaned_data['date_type'] == 'date_range':
                start = form.cleaned_data['start']
                end = form.cleaned_data['end']
            else:
                now = datetime.now()
                start = now - timedelta(days=int(form.cleaned_data['last_days']))
                end = now
            show_most_recent_note = form.cleaned_data['most_recent_note']
            group_by = form.cleaned_data['group_by']
            # sort_by = form.cleaned_data['sort_by']
            show_empty = form.cleaned_data['show_empty']
            if form.cleaned_data['show_all_statuses']:
                statuses = JobStatus.objects.all()
            else:
                statuses = form.cleaned_data['statuses']
                statuses = JobStatus.objects.filter(status__in=statuses)
            objects = 0
            if group_by == 'Adjuster':
                return by_fk(request, start, end, show_empty, show_most_recent_note, statuses, Adjuster, 'name', 'adjuster')
            elif group_by == 'Entry Date':
                return by_entry_date(request, start, end, show_empty, show_most_recent_note, statuses)
            elif group_by == 'Estimator':
                return by_user_group(request, start, end, show_empty, show_most_recent_note, statuses, 'Estimators', 'estimator', 'job_estimator')
            elif group_by == 'Superintendent':
                return by_user_group(request, start, end, show_empty, show_most_recent_note, statuses, 'Superintendents', 'super', 'job_super')
            elif group_by == 'InsuranceCo':
                return by_fk(request, start, end, show_empty, show_most_recent_note, statuses, Insurance, 'name', 'insurance_company')
            elif group_by == 'LossType':
                return by_fk(request, start, end, show_empty, show_most_recent_note, statuses, LossType, 'loss_type', 'loss_type')
            elif group_by == 'Program':
                return by_fk(request, start, end, show_empty, show_most_recent_note, statuses, ProgramType, 'type', 'program_type')
            elif group_by == 'Referral':
                return by_fk(request, start, end, show_empty, show_most_recent_note, statuses, ReferralType, 'referral_type', 'referral_type')
            elif group_by == 'Status':
                return by_fk(request, start, end, show_empty, show_most_recent_note, statuses, JobStatus, 'status', 'status')
            else:
                raise ValueError('Unexpected input from cleaned form')
    else:
        return render(request, "report.html", {'form': Report()})


@login_required()
def email_doc(request):
    if request.method == 'POST' and request.POST:
        form = EmailObjs(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            to = form.cleaned_data['to']
            cc = form.cleaned_data['cc']
            bcc = form.cleaned_data['bcc']
            body = form.cleaned_data['body']
            document_pks = [int(token) for token in form.cleaned_data['obj_ids'].split(',')]
            docs = Document.objects.filter(pk__in=document_pks)
            email = EmailMessage(subject=subject,
                                 body=body,
                                 from_email=request.user.email,
                                 to=to,
                                 cc=cc,
                                 bcc=bcc,)
            for doc in docs:
                email.attach_file(doc.file.path)
            email.send()
            messages.add_message(request, messages.SUCCESS, ("Email Sent!"))
            return HttpResponseRedirect(reverse('admin:coversheets_document_changelist'))
        else:
            return render(request, "email_obj.html", {'form': form, 'form_url': reverse('email_doc')})
    else:
        try:
            doc_id_list = request.GET.get('ids')
            doc_ids = [int(doc_id) for doc_id in doc_id_list.split(',')]
        except AttributeError:
            messages.add_message(request, messages.ERROR, ("No documents selected!"))
            return HttpResponseRedirect(reverse('admin:coversheets_document_changelist'))
        except ValueError:
            messages.add_message(request, messages.ERROR, ("Bad URL parameters!"))
            return HttpResponseRedirect(reverse('admin:coversheets_document_changelist'))
        if request.GET.get('_popup') and request.GET.get('_popup') == '1':
            popup = True
        else:
            popup = False

        docs = Document.objects.filter(pk__in=doc_ids)
        body = "----------------------\nAttachments:\n\n" + "\n".join([(doc.verbose_str()) for doc in docs])
        form = EmailObjs({'obj_ids': doc_id_list,
                              'subject': "[Job {}][Documents]".format(docs[0].jobsheet),
                              'to': request.user.email,
                              'body': body})
        return render(request, "email_obj.html", {'form': form,
                                                       'is_popup': popup,
                                                       'form_url': reverse('email_doc')})


@login_required()
def email_pics(request):
    if request.method == 'POST' and request.POST:
        form = EmailObjs(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            to = form.cleaned_data['to']
            cc = form.cleaned_data['cc']
            bcc = form.cleaned_data['bcc']
            body = form.cleaned_data['body']
            image_pks = [int(token) for token in form.cleaned_data['obj_ids'].split(',')]
            imgs = Image.objects.filter(pk__in=image_pks)
            email = EmailMessage(subject=subject,
                                 body=body,
                                 from_email=request.user.email,
                                 to=to,
                                 cc=cc,
                                 bcc=bcc,)
            for img in imgs:
                email.attach_file(img.image_file.path)
            email.send()
            messages.add_message(request, messages.SUCCESS, ("Email Sent!"))
            return HttpResponseRedirect(reverse('admin:coversheets_image_changelist'))
        else:
            return render(request, "email_obj.html", {'form': form, 'form_url': reverse('email_pic')}, )
    else:
        try:
            image_id_list = request.GET.get('ids')
            image_ids = [int(image_id) for image_id in image_id_list.split(',')]
        except AttributeError:
            messages.add_message(request, messages.ERROR, ("No emails selected!"))
            return HttpResponseRedirect(reverse('admin:coversheets_image_changelist'))
        except ValueError:
            messages.add_message(request, messages.ERROR, ("Bad URL parameters!"))
            return HttpResponseRedirect(reverse('admin:coversheets_image_changelist'))
        if request.GET.get('_popup') and request.GET.get('_popup') == '1':
            popup = True
        else:
            popup = False

        imgs = Image.objects.filter(pk__in=image_ids)
        body = "----------------------\n" + str(len(imgs)) + " images attached"
        subject = "[Images]"
        form = EmailObjs({'obj_ids': image_id_list,
                              'subject': subject,
                              'to': request.user.email,
                              'body': body})
        return render(request, "email_obj.html", {'form': form,
                                                       'is_popup': popup,
                                                       'form_url': reverse('email_pic')})
@login_required()
def print_job(request, job_id):
    return print_job_with_notes(request, job_id, print_notes=False)

@login_required()
def print_job_with_notes(request, job_id, print_notes=True):
    job = Job.objects.get(pk=job_id)
    return render(request, "print_job.html", {'job': job, 'show_notes': print_notes})