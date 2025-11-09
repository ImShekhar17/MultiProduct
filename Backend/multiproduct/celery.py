import os
from celery import Celery
from django.conf import settings
import multiprocessing


multiprocessing.set_start_method('spawn', True)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multiproduct.settings")

app = Celery("multiproduct")

app.conf.enable_utc = False

app.config_from_object('django.conf:settings', namespace="CELERY")

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
