from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from . import models


@admin.register(models.Worker)
class WorkerAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Resource)
class ResourceAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Instance)
class InstanceAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'resource',
        'worker',
        'slots',
        'free',
    )
    list_filter = (
        'resource',
        'worker',
    )


class JobConstraintInline(admin.TabularInline):
    model = models.JobConstraint


@admin.register(models.Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'worker',
        'running',
        'started',
        'finished',
    )
    list_filter = (
        'worker',
        'running',
        'started',
        'finished',
    )
    date_hierarchy = "started"
    view_on_site = False
    inlines = [
        JobConstraintInline,
    ]
    readonly_fields = (
        "id",
        "running",
        "started",
        "finished",
    )
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'id',
                    'worker',
                    'script',
                    'environment',
                )
            }
        ),
        (
            _('State'),
            {
                'classes': ('collapse',),
                'fields': (
                    "running",
                    "started",
                    "finished",
                ),
            }
        ),
    )
