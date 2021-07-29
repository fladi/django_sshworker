import random
import stat
import uuid
import paramiko
from collections import ChainMap
from django.db import models
from django.contrib.postgres.fields import ArrayField, HStoreField
from django.template import Context, Template
from django.utils import timezone
from io import StringIO
from base64 import decodebytes
from paramiko.client import SSHClient, RejectPolicy
from paramiko.hostkeys import HostKeyEntry

from .conf import settings


class Worker(models.Model):
    hostname = models.CharField(max_length=256)
    port = models.PositiveIntegerField(default=22)
    username = models.CharField(max_length=256)
    host_key = models.TextField()
    private_key = models.TextField()
    active = models.BooleanField(default=False)

    KEY_TYPES = {
        paramiko.dsskey.DSSKey: (
            "ssh-dss",
        ),
        paramiko.ed25519key.Ed25519Key: (
            "ssh-ed25519",
        ),
        paramiko.rsakey.RSAKey: (
            "ssh-rsa",
        ),
        paramiko.ecdsakey.ECDSAKey: (
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
        )
    }

    def __str__(self):
        return f"{self.username}@{self.hostname}"

    def get_private_key(self):
        # Stupid hack because paramiko does not offer autodetection of keys
        for klass in self.KEY_TYPES.keys():
            try:
                return klass.from_private_key(StringIO(self.private_key))
            except:
                pass
        raise Exception("Private key could not be loaded")

    def get_host_key(self):
        # Stupid hack because paramiko does not offer autodetection of keys
        prefix, key = self.host_key.split()
        for klass, match in self.KEY_TYPES.items():
            if prefix in match:
                return klass(data=decodebytes(key.encode("ascii")))
        raise Exception("Host key could not be loaded")

    def fit(self, resource, slots):
        instances = list(filter(
            lambda i: i.free >= slots,
            self.instance_set.filter(resource=resource)
        ))
        if not instances:
            return
        return random.choice(instances)

    def connect(self):
        host_key = self.get_host_key()
        client = SSHClient()
        client.get_host_keys().add(
            self.hostname,
            host_key.get_name(),
            host_key
        )
        client.set_missing_host_key_policy(RejectPolicy)
        client.connect(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            pkey=self.get_private_key(),
            timeout=settings.SSHWORKER_TIMEOUT,
            allow_agent=False,
            look_for_keys=False
        )
        return client


class Resource(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Instance(models.Model):
    name = models.CharField(max_length=256)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    slots = models.PositiveIntegerField()
    properties = HStoreField()

    def __str__(self):
        return f"{self.name}: {self.resource}[{self.worker}]"

    @property
    def free(self):
        occupied = self.jobconstraint_set.filter(job__running=True).aggregate(
            required=models.Sum('required')
        ).get('required') or 0
        return self.slots - occupied


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, blank=True, null=True)
    script = models.TextField(null=False, blank=False)
    environment = HStoreField(
        blank=True,
        null=True,
    )
    running = models.BooleanField(default=False)
    started = models.DateTimeField(blank=True, null=True)
    finished = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}: {self.worker}"

    @property
    def unit(self):
        return f"job.{self.id}"

    @property
    def tempfile(self):
        return f"/tmp/{self.unit}"

    def assign(self):
        workers = Worker.objects.filter(
            active=True,
            instance__resource_id__in=self.jobconstraint_set.values_list('resource', flat=True).distinct()
        ).distinct()
        for w in random.sample(list(workers), len(workers)):
            instances = dict(map(
                lambda jc: (jc, w.fit(jc.resource, jc.required)),
                self.jobconstriant_set.all()
            ))
            if all(instances.values()):
                self.worker = w
                for jc in self.jobconstraint_set.all():
                    jc.instance = instances.get(jc)
                    jc.save()
                self.save()
                return True
        return False

    def start(self):
        if not self.worker:
            return False

        with self.instance.worker.connect() as ssh:
            with ssh.open_sftp() as sftp:
                with sftp.file(self.tempfile, 'w') as script:
                    script.write(self.script)
            with ssh.get_transport() as transport:
                with transport.open_session() as session:
                    session.exec_command(" ".join(
                        "systemd-run",
                        "--user",
                        "-r",
                        "-p", "Type=exec",
                        "-u", self.unit,
                        self.tempfile
                    ))
                    status = session.recv_exit_status()
                    if status != 0:
                        raise Exception(f"Failed to create service unit for {self.id}: {status}")
        self.running = True
        self.started = timezone.now()
        self.save()

    def stop(self):
        with self.instance.worker.connect() as ssh:
            with ssh.open_sftp() as sftp:
                sftp.unlink(self.tempfile)
            with ssh.get_transport() as transport:
                with transport.open_session() as session:
                    session.exec_command(" ".join(
                        "systemctl",
                        "--user",
                        "stop",
                        self.unit,
                    ))
                    status = session.recv_exit_status()
                    if status != 0:
                        raise Exception(f"Failed to stop service unit for {self.id}: {status}")
        self.running = False
        self.finished = timezone.now()
        self.save()

    def is_alive(self):
        with self.instance.worker.connect() as ssh:
            with ssh.get_transport() as transport:
                with transport.open_session() as session:
                    session.exec_command(" ".join(
                        "systemctl",
                        "--user",
                        "status",
                        self.unit,
                    ))
                    if session.recv_exit_status() == 0:
                        return True
                    self.running = False
                    self.save()
                    return False


class JobConstraint(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE, blank=True, null=True)
    required = models.PositiveIntegerField(default=1)
