# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0012_remove_job_album'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='album',
            name='jobsheet',
        ),
        migrations.AddField(
            model_name='album',
            name='job',
            field=models.ForeignKey(related_name='job', blank=True, to='coversheets.Job', null=True),
            preserve_default=True,
        ),
    ]
