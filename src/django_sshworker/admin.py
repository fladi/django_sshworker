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
    pass


class JobConstraintInline(admin.TabularInline):
    model = models.JobConstraint


@admin.register(models.Job)
class JobAdmin(admin.ModelAdmin):
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
