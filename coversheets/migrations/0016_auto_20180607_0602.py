# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0015_auto_20150701_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='entry_date',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='status',
            field=models.ForeignKey(to='coversheets.JobStatus', null=True),
            preserve_default=True,
        ),
    ]
