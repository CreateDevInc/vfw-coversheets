# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0025_auto_20180829_0825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='loss_year_built',
            field=models.CharField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
    ]
