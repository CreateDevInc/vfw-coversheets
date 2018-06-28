from django import template
from django.contrib.admin.models import LogEntry
from cuser.middleware import CuserMiddleware
from ..models import Job

register = template.Library()

def show_recent_jobs():
    current_user = CuserMiddleware.get_user()
    log = LogEntry.objects.select_related().all().order_by('-id')[:10]
    return {
        'log': log,
        'current_user': current_user
    }
register.inclusion_tag('recent_jobs.html')(show_recent_jobs)
