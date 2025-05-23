from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "letosite.settings")

app = Celery("letosite")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.timezone = 'Asia/Yekaterinburg'
app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
