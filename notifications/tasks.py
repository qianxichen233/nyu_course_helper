from __future__ import absolute_import, unicode_literals

from celery import shared_task
from mainapp.models import *
from .course_crawler import crawler
import time


@shared_task
def run():
	new_crawler=crawler()
	new_crawler.update_database()