# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0003_auto_20150515_1659'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='do_we_collect',
        ),
        migrations.RemoveField(
            model_name='job',
            name='po_number',
        ),
    ]
