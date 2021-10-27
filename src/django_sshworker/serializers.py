from rest_framework import serializers


from . import models


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Worker
        fields = ["id", "hostname", "port", "host_key", "private_key"]


class JobSerializer(serializers.ModelSerializer):
    worker = WorkerSerializer(source="instance__worker")

    class Meta:
        model = models.Job
        fields = [
            "id",
            "worker",
            "environment",
            "command",
            "running",
            "returncode",
            "scheduled",
            "finished",
            "processing",
            "filter",
        ]
