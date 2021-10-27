# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-05-19 10:51
from __future__ import unicode_literals

import django.contrib.postgres.fields.hstore
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Instance",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=256)),
                ("slots", models.PositiveIntegerField()),
                ("properties", django.contrib.postgres.fields.hstore.HStoreField()),
            ],
        ),
        migrations.CreateModel(
            name="Job",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("script", models.TextField()),
                (
                    "environment",
                    django.contrib.postgres.fields.hstore.HStoreField(
                        blank=True, null=True
                    ),
                ),
                ("running", models.BooleanField(default=False)),
                ("started", models.DateTimeField(blank=True, null=True)),
                ("finished", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="JobConstraint",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("required", models.PositiveIntegerField(default=1)),
                (
                    "instance",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="django_sshworker.Instance",
                    ),
                ),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="django_sshworker.Job",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Resource",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name="Worker",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("hostname", models.CharField(max_length=256)),
                ("port", models.PositiveIntegerField(default=22)),
                ("username", models.CharField(max_length=256)),
                ("host_key", models.TextField()),
                ("private_key", models.TextField()),
                ("active", models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name="jobconstraint",
            name="resource",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="django_sshworker.Resource",
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="worker",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="django_sshworker.Worker",
            ),
        ),
        migrations.AddField(
            model_name="instance",
            name="resource",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="django_sshworker.Resource",
            ),
        ),
        migrations.AddField(
            model_name="instance",
            name="worker",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="django_sshworker.Worker",
            ),
        ),
    ]
