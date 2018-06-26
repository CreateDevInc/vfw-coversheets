# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_localflavor_us.models


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0016_auto_20180607_0602'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='album_link',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='budget_link',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='estimated_completion_date',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='loss_year_built',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='pending_items',
            field=models.CharField(max_length=1000, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='percent_complete',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='production_start_date',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='program_due_date',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='called_in_by',
            field=models.CharField(max_length=200, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='customer',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='entry_date',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='loss_address',
            field=models.CharField(max_length=128, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='loss_city',
            field=models.ForeignKey(related_name='job_city_loss', blank=True, to='cities_light.City'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='loss_type',
            field=models.ForeignKey(to='coversheets.LossType', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='loss_zip',
            field=models.CharField(max_length=10, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='primary_phone',
            field=django_localflavor_us.models.PhoneNumberField(max_length=20, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='program_type',
            field=models.ForeignKey(to='coversheets.ProgramType', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='referral_type',
            field=models.ForeignKey(blank=True, to='coversheets.ReferralType', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='status',
            field=models.ForeignKey(blank=True, to='coversheets.JobStatus', null=True),
            preserve_default=True,
        ),
    ]
