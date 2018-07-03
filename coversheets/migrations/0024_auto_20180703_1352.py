# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0023_auto_20180627_1724'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='ind_insurance_company',
            field=models.ForeignKey(related_name='ind_insurance_company', blank=True, to='coversheets.Insurance', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='customer',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
