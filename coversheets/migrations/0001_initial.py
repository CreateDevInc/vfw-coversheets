# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields
from django.conf import settings
import cuser.fields
import django_localflavor_us.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cities_light', '0003_auto_20141120_0342'),
    ]

    operations = [
        migrations.CreateModel(
            name='Adjuster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('phone', django_localflavor_us.models.PhoneNumberField(max_length=20, blank=True)),
                ('fax', django_localflavor_us.models.PhoneNumberField(max_length=20, blank=True)),
                ('mobile', django_localflavor_us.models.PhoneNumberField(max_length=20, blank=True)),
                ('email', models.EmailField(max_length=75, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=255, blank=True)),
                ('description', models.CharField(default=b'', max_length=2048, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(max_length=1024, blank=True)),
                ('file', models.FileField(upload_to=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocumentSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image_file', sorl.thumbnail.fields.ImageField(upload_to=b'photos')),
                ('description', models.CharField(default=b'', max_length=2048, blank=True)),
                ('album', models.ForeignKey(to='coversheets.Album', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Insurance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('info_entered_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('info_updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('entry_date', models.DateTimeField()),
                ('add_job_number', models.BooleanField(default=False)),
                ('job_number', models.PositiveIntegerField(unique=True, null=True, blank=True)),
                ('called_in_by', models.CharField(max_length=200)),
                ('estimated_loss', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('referred_by', models.CharField(max_length=255, blank=True)),
                ('customer', models.CharField(max_length=255)),
                ('customer_email', models.EmailField(max_length=75, blank=True)),
                ('contact', models.CharField(max_length=255)),
                ('contact_email', models.EmailField(max_length=75, blank=True)),
                ('primary_phone', django_localflavor_us.models.PhoneNumberField(max_length=20)),
                ('mobile_phone', django_localflavor_us.models.PhoneNumberField(max_length=20, blank=True)),
                ('address', models.CharField(max_length=128, null=True, blank=True)),
                ('zip', models.CharField(max_length=10, null=True, blank=True)),
                ('loss_address', models.CharField(max_length=128)),
                ('loss_zip', models.CharField(max_length=10)),
                ('directions', models.TextField(max_length=4000, blank=True)),
                ('claim_date', models.DateField(null=True, blank=True)),
                ('claim_number', models.CharField(max_length=255, blank=True)),
                ('deductible', models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True)),
                ('deductible_collected', models.BooleanField(default=False)),
                ('policy_number', models.CharField(max_length=255, blank=True)),
                ('do_we_collect', models.BooleanField(default=False)),
                ('emergency_requested', models.BooleanField(default=False)),
                ('po_number', models.CharField(max_length=255, blank=True)),
                ('emergency_dispatch', models.CharField(max_length=255, blank=True)),
                ('additional_info', models.TextField(max_length=4000, blank=True)),
                ('adjuster', models.ForeignKey(blank=True, to='coversheets.Adjuster', null=True)),
                ('album', models.OneToOneField(null=True, blank=True, to='coversheets.Album')),
                ('city', models.ForeignKey(related_name='job_city_customer', blank=True, to='cities_light.City', null=True)),
                ('estimator', models.ForeignKey(related_name='job_estimator', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('info_taken_by', cuser.fields.CurrentUserField(related_name='created_job', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('info_updated_by', cuser.fields.CurrentUserField(related_name='updated_job', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('insurance_company', models.ForeignKey(blank=True, to='coversheets.Insurance', null=True)),
                ('loss_city', models.ForeignKey(related_name='job_city_loss', to='cities_light.City')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Job Statuses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LossType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('loss_type', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('comment', models.TextField(max_length=10000)),
                ('cc1', models.EmailField(max_length=75, null=True, blank=True)),
                ('cc2', models.EmailField(max_length=75, null=True, blank=True)),
                ('created_by', cuser.fields.CurrentUserField(related_name='created_note', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('jobsheet', models.ForeignKey(to='coversheets.Job')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProgramType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReferralType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('referral_type', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='job',
            name='loss_type',
            field=models.ForeignKey(to='coversheets.LossType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='production_manager',
            field=models.ForeignKey(related_name='job_project_manager', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='program_type',
            field=models.ForeignKey(to='coversheets.ProgramType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='referral_type',
            field=models.ForeignKey(to='coversheets.ReferralType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='status',
            field=models.ForeignKey(to='coversheets.JobStatus'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='super',
            field=models.ForeignKey(related_name='job_super', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='jobsheet',
            field=models.ForeignKey(to='coversheets.Job'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='source',
            field=models.ForeignKey(to='coversheets.DocumentSource', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='type',
            field=models.ForeignKey(to='coversheets.DocumentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='adjuster',
            name='insurance_company',
            field=models.ForeignKey(to='coversheets.Insurance', null=True),
            preserve_default=True,
        ),
    ]
