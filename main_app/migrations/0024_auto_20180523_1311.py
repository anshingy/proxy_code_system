# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0023_auto_20180523_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authorization',
            name='proxy_man',
            field=models.ForeignKey(verbose_name='代理', blank=True, null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
