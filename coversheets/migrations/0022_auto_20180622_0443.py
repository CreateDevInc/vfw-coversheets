# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0021_auto_20180621_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adjuster',
            name='adjuster_type',
            field=models.ForeignKey(to='coversheets.AdjusterType', null=True),
            preserve_default=True,
        ),
    ]
