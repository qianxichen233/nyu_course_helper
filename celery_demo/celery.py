from __future__ import absolute_import, unicode_literals

from celery import Celery
from datetime import datetime, timedelta

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'celery_demo.settings')

app = Celery('celery_demo')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'crawler': {
        'task': 'notifications.tasks.run',
        'schedule': 3000.0,
    }
}

app.conf.timezone = 'UTC'

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
