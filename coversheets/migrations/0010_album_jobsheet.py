# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coversheets', '0009_document_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='jobsheet',
            field=models.ForeignKey(related_name='jobsheet', blank=True, to='coversheets.Job', null=True),
            preserve_default=True,
        ),
    ]
