# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-03-14 15:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0003_auto_20200312_2157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='avatar',
            field=models.CharField(default=1, max_length=64, verbose_name='头像'),
            preserve_default=False,
        ),
    ]