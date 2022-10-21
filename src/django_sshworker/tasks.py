from celery import shared_task

from .models import Worker


@shared_task
def check_worker_online():
    for worker in Worker.ojects.filter(active=True):
        try:
            worker.connect()
        except Exception:
            if not worker.online:
                continue
            worker.online = False
        else:
            if worker.online:
                continue
            worker.online = True
        worker.save()
