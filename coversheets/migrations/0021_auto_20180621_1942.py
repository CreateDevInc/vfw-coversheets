# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0020_auto_20180607_0815'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='independent_adjuster',
            field=models.ForeignKey(related_name='independent_adjuster', blank=True, to='coversheets.Adjuster', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='schedule_link',
            field=models.CharField(max_length=512, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='budget_link',
            field=models.CharField(max_length=512, null=True, blank=True),
            preserve_default=True,
        ),
    ]
