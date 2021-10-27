from appconf import AppConf
from django.conf import settings


class SSHWorkerAppConf(AppConf):
    TIMEOUT = 10

    class Meta:
        prefix = "SSHWORKER"
