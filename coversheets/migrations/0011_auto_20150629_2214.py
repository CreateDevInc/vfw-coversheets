# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from coversheets.models import Job

def move_albums(apps, schema_editor):
    if hasattr(Job, 'album'):
        for job in Job.objects.filter(album__isnull=False):
            job.album.jobsheet = job.album.id
            job.save()

class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0010_album_jobsheet'),
    ]

    operations = [
        migrations.RunPython(move_albums),
    ]
