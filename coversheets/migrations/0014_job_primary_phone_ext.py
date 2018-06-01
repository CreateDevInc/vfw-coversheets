# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0013_auto_20150629_2221'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='primary_phone_ext',
            field=models.CharField(max_length=64, blank=True),
            preserve_default=True,
        ),
    ]
