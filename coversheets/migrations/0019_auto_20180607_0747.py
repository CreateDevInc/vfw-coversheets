# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0018_auto_20180607_0739'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdjusterType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('adjuster_type', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['adjuster_type'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='adjuster',
            name='adjuster_type',
            field=models.ForeignKey(blank=True, to='coversheets.AdjusterType', null=True),
            preserve_default=True,
        ),
    ]
