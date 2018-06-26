# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0017_auto_20180607_0733'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='directions',
            new_name='loss_information',
        ),
    ]
