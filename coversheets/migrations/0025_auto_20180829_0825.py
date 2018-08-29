# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0024_auto_20180703_1352'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adjuster',
            name='adjuster_type',
        ),
        migrations.AddField(
            model_name='job',
            name='adjuster_type_1',
            field=models.ForeignKey(related_name='adjuster_type_1', to='coversheets.AdjusterType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='adjuster_type_2',
            field=models.ForeignKey(related_name='adjuster_type_2', to='coversheets.AdjusterType', null=True),
            preserve_default=True,
        ),
    ]
