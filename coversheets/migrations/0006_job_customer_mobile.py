# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_localflavor_us.models


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0005_job_customer_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='customer_mobile',
            field=django_localflavor_us.models.PhoneNumberField(max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
    ]
