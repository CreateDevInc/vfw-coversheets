from django import template
from django.contrib.admin.models import LogEntry
from ..models import Job

register = template.Library()

def show_recent_jobs():
    log = LogEntry.objects.select_related().all().order_by('-id')[:10]
    return {'jobs': Job.objects.all(), 'log': log}
register.inclusion_tag('recent_jobs.html')(show_recent_jobs)
