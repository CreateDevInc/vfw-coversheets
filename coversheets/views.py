from datetime import timedelta, datetime, time
from django.db import models
from django.contrib.auth.models import User
from django.views.generic.list import ListView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from forms import AlbumUpload, Report, EmailObjs
from models import Image, Job, Adjuster, JobStatus, User, Insurance, LossType, ProgramType, ReferralType, Document
from itertools import groupby
from operator import itemgetter
from pytz import timezone
from numpy import mean, amax, amin, sum


def home(request):
    return HttpResponse('Hello world')

@login_required()
def show_album(request, album):
    context = {}
    context['images'] = Image.objects.filter(album=album)
    return render(request, 'show_album.html', context)

@login_required()
def add_album(request):
    if request.method == 'POST' and request.POST:
        form = AlbumUpload(request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
        return render(request, 'multi_upload_template.html', {'form': form})
    else:
        return render(request, 'multi_upload_template.html', {'form': AlbumUpload()})

def get_object_name(name):
    names = {
        'InsuranceCo': 'insurance_company',
        'Adjuster': 'adjuster',
        'Estimator': 'estimator',
        'Production Manager': 'production_manager',
        'Superintendent': 'super',
        'LossType': 'loss_type',
        'Program': 'program_type',
        'Referral': 'referred_by',
        'Status': 'status',
        'Entry Date': 'entry_date',
    }
    return names[name]

def get_jobs_stat(groups, stat):
    vals = []
    count = 0
    if len(groups) > 0 and isinstance(groups[0], Job):
        for job in groups:
            count += 1
            if job.estimated_loss is not None:
                vals.append(job.estimated_loss)
    else:
        for group in groups:
            for job in group['jobs']:
                count += 1
                if job.estimated_loss is not None:
                    vals.append(job.estimated_loss)
    if len(vals) < 1 and stat is not 'count':
        return None
    if stat == 'avg':
        return mean(vals)
    if stat == 'max':
        return amax(vals)
    if stat == 'min':
        return amin(vals)
    if stat == 'sum':
        return sum(vals)
    if stat == 'count':
        return count

def get_job_attr(job, obj_name):
    if obj_name == 'entry_date':
        return job.entry_date.strftime('%b %d, %Y')
    else:
        return getattr(job, obj_name)

def group_jobs(jobs, group_by):
    groups = {}
    obj_name = get_object_name(group_by)

    for job in jobs:
        if get_job_attr(job, obj_name) not in groups:
            groups[get_job_attr(job, obj_name)] = [job]
        else:
            groups[get_job_attr(job, obj_name)].append(job)

    return groups

def sort_jobs(jobs, sort_by):
    sorted_groups = {}
    obj_name = get_object_name(sort_by)

    for k, v in jobs.iteritems():
        if k not in sorted_groups:
            sorted_groups[k] = {}
        for job in v:
            if get_job_attr(job, obj_name) not in sorted_groups[k]:
                sorted_groups[k][get_job_attr(job, obj_name)] = [job]
            else:
                sorted_groups[k][get_job_attr(job, obj_name)].append(job)
    return sorted_groups

def get_jobs(group_by, sort_by, start, end, statuses, show_empty=False):
    jobs = Job.objects.filter(
        entry_date__gt=start,
        entry_date__lt=end,
        status__in=statuses).select_related(
            'estimator',
            'super',
            'production_manager',
            'insurance_company',
            'adjuster',
            'status',
            'loss_type',
            'program_type',
            'referral_type'
        )
    job_groups = group_jobs(jobs, group_by)
    job_groups = sort_jobs(job_groups, sort_by)
    if not show_empty:
        job_groups.pop(None, None)
        for k, v in job_groups.iteritems():
            v.pop(None, None)
    return job_groups

def sort_jobs_for_template(jobs, group_by_date, sort_by_date):
    sorted_jobs = []
    if group_by_date:
        sorted_keys = sorted(
            jobs, key=lambda x: datetime.strptime(x, '%b %d, %Y')
        )
    else:
        sorted_keys = sorted(jobs)
    for k in sorted_keys:
        new_group = []
        if sort_by_date:
            sorted_sub_keys = sorted(
                jobs[k], key=lambda x: datetime.strptime(x, '%b %d, %Y')
            )
        else:
            sorted_sub_keys = sorted(jobs[k])
        for kk in sorted_sub_keys:
            new_group.append({
                'job_count': get_jobs_stat(jobs[k][kk], 'count'),
                'avg': get_jobs_stat(jobs[k][kk], 'avg'),
                'sum': get_jobs_stat(jobs[k][kk], 'sum'),
                'max': get_jobs_stat(jobs[k][kk], 'max'),
                'min': get_jobs_stat(jobs[k][kk], 'min'),
                'name': kk,
                'jobs': jobs[k][kk]
            })
        sorted_jobs.append({
            'job_count': get_jobs_stat(new_group, 'count'),
            'avg': get_jobs_stat(new_group, 'avg'),
            'sum': get_jobs_stat(new_group, 'sum'),
            'max': get_jobs_stat(new_group, 'max'),
            'min': get_jobs_stat(new_group, 'min'),
            'name': k,
            'jobs': new_group
        })
    return sorted_jobs

@login_required()
def weekly_production(request):
    now = datetime.now()
    start = now - timedelta(days=7)
    end = now
    show_most_recent_note = False
    group_by = 'Production Manager'
    sort_by = 'Estimator'
    show_empty = True
    statuses = JobStatus.objects.all()
    jobs = get_jobs(group_by, sort_by, start, end, statuses, show_empty)

    try:
        jobs = get_jobs(group_by, sort_by, start, end, statuses, show_empty)
    except Exception, e:
        raise ValueError('There was a problem generating this report. Please try again or contact support.')

    return render(request, 'weekly_production.html', {
        'job_groups': sort_jobs_for_template(jobs, False, False),
        'start': start,
        'end': end,
        'group_by': group_by,
        'sort_by': sort_by,
        'show_most_recent_note': show_most_recent_note
    })

@login_required()
def estimator_snapshot(request):
    now = datetime.now()
    start = now - timedelta(days=365)
    end = now
    show_most_recent_note = False
    group_by = 'Estimator'
    sort_by = 'InsuranceCo'
    show_empty = False
    statuses = JobStatus.objects.filter(status__in=[
        'Assigned', 'Emergency', 'Pending', 'Signed'
    ])
    jobs = get_jobs(group_by, sort_by, start, end, statuses, show_empty)

    try:
        jobs = get_jobs(group_by, sort_by, start, end, statuses, show_empty)
    except Exception, e:
        raise ValueError('There was a problem generating this report. Please try again or contact support.')

    return render(request, 'estimator_snapshot.html', {
        'job_groups': sort_jobs_for_template(jobs, False, False),
        'start': start,
        'end': end,
        'group_by': group_by,
        'sort_by': sort_by,
        'show_most_recent_note': show_most_recent_note
    })

@login_required()
def warranty_list(request):
    now = datetime.now()
    start = now - timedelta(days=365)
    end = now
    show_most_recent_note = False
    group_by = 'Production Manager'
    sort_by = 'Entry Date'
    show_empty = True
    statuses = JobStatus.objects.filter(status__in=['Warranty'])
    jobs = get_jobs(group_by, sort_by, start, end, statuses, show_empty)

    try:
        jobs = get_jobs(group_by, sort_by, start, end, statuses, show_empty)
    except Exception, e:
        raise ValueError('There was a problem generating this report. Please try again or contact support.')

    return render(request, 'warranty_list.html', {
        'job_groups': sort_jobs_for_template(jobs, False, True),
        'start': start,
        'end': end,
        'group_by': group_by,
        'sort_by': sort_by,
        'show_most_recent_note': show_most_recent_note
    })

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
            sort_by = form.cleaned_data['sort_by']
            show_empty = form.cleaned_data['show_empty']
            if form.cleaned_data['show_all_statuses']:
                statuses = JobStatus.objects.all()
            else:
                statuses = form.cleaned_data['statuses']
                statuses = JobStatus.objects.filter(status__in=statuses)

            try:
                jobs = get_jobs(group_by, sort_by, start, end, statuses, show_empty)
            except Exception, e:
                raise ValueError('There was a problem generating this report. Please try again or contact support.')

            return render(request, 'job_list.html', {
                'job_groups': sort_jobs_for_template(
                    jobs,
                    group_by=='Entry Date',
                    sort_by=='Entry Date'
                ),
                'start': start,
                'end': end,
                'group_by': group_by,
                'sort_by': sort_by,
                'show_most_recent_note': show_most_recent_note
            })
    else:
        return render(request, 'report.html', {'form': Report()})


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

@login_required()
def get_job_number(request):
    # Get the last Job with a job number and increment one for new job number
    # NOTE: This isn't ideal - job_number should *always* be set by the database
    # and auto-incremented
    job = Job.objects.exclude(job_number__isnull=True).order_by('-job_number')[0]
    return JsonResponse({'job_number': job.job_number + 1})
