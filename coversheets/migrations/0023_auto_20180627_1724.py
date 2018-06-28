# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django_localflavor_us.models


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0022_auto_20180622_0443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='additional_info',
            field=models.TextField(max_length=4000, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='claim_number',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='contact_info_1_ext',
            field=models.CharField(max_length=64, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='contact_info_2_ext',
            field=models.CharField(max_length=64, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='customer_email',
            field=models.EmailField(max_length=75, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='emergency_dispatch',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='entry_date',
            field=models.DateTimeField(default=datetime.datetime.now, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='loss_address',
            field=models.CharField(max_length=128, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='loss_city',
            field=models.ForeignKey(related_name='job_city_loss', blank=True, to='cities_light.City', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='loss_information',
            field=models.TextField(max_length=4000, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='loss_type',
            field=models.ForeignKey(blank=True, to='coversheets.LossType', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='loss_zip',
            field=models.CharField(max_length=10, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='mobile_phone',
            field=django_localflavor_us.models.PhoneNumberField(max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='mobile_phone_ext',
            field=models.CharField(max_length=64, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='policy_number',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='primary_phone_ext',
            field=models.CharField(max_length=64, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='program_type',
            field=models.ForeignKey(blank=True, to='coversheets.ProgramType', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='job',
            name='referred_by',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
