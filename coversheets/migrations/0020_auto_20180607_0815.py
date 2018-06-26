# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0019_auto_20180607_0747'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='customer_phone',
            new_name='contact_info_1',
        ),
        migrations.RenameField(
            model_name='job',
            old_name='customer_phone_ext',
            new_name='contact_info_1_ext',
        ),
        migrations.RenameField(
            model_name='job',
            old_name='customer_mobile',
            new_name='contact_info_2',
        ),
        migrations.RenameField(
            model_name='job',
            old_name='customer_mobile_ext',
            new_name='contact_info_2_ext',
        ),
        migrations.RenameField(
            model_name='job',
            old_name='address',
            new_name='customer_address',
        ),
    ]
