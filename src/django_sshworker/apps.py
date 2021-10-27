from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SSHWorkerConfig(AppConfig):
    name = "django_sshworker"
    verbose_name = _("SSH Workers")
