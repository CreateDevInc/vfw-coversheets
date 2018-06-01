# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0014_job_primary_phone_ext'),
    ]

    operations = [
        migrations.AddField(
            model_name='adjuster',
            name='fax_ext',
            field=models.CharField(max_length=64, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='adjuster',
            name='mobile_ext',
            field=models.CharField(max_length=64, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='adjuster',
            name='phone_ext',
            field=models.CharField(max_length=64, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='customer_mobile_ext',
            field=models.CharField(max_length=64, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='customer_phone_ext',
            field=models.CharField(max_length=64, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='mobile_phone_ext',
            field=models.CharField(max_length=64, blank=True),
            preserve_default=True,
        ),
    ]
