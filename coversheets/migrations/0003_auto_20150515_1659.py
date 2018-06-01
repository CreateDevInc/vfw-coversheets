# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0002_auto_20150510_0050'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adjuster',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='insurance',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='jobstatus',
            options={'ordering': ['status'], 'verbose_name_plural': 'Job Statuses'},
        ),
        migrations.AlterModelOptions(
            name='losstype',
            options={'ordering': ['loss_type']},
        ),
        migrations.AlterModelOptions(
            name='programtype',
            options={'ordering': ['type']},
        ),
        migrations.AlterModelOptions(
            name='referraltype',
            options={'ordering': ['referral_type']},
        ),
        migrations.AlterField(
            model_name='job',
            name='estimated_loss',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True),
            preserve_default=True,
        ),
    ]
