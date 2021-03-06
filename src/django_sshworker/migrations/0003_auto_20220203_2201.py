# Generated by Django 2.2.24 on 2022-02-03 21:01

import django.contrib.postgres.fields.hstore
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_sshworker', '0002_auto_20210519_1504'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='job',
            options={'ordering': ('started', 'finished')},
        ),
        migrations.AddField(
            model_name='worker',
            name='properties',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True),
        ),
    ]
