__name__ = 'issue_to_story_sync'
__version__ = '1.0.0'

from flask import Flask

import atexit
import datetime
import json
import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

application = Flask(__name__)
scheduler = BackgroundScheduler()

from views import create_jobs, index


def init():
    load_config()
    schedule_jobs()


def load_config():

    application.config.update({'CONFIG_NAME':os.environ['CONFIG_NAME']})

    basepath = os.path.dirname(__file__)
    filepath = os.path.abspath(os.path.join(basepath, '..', application.config['CONFIG_NAME']))
    f = open(filepath, 'r')
    application.config.update(json.loads(f.read()))

    # basic logging config required for apscheduler
    logging.basicConfig()


def schedule_jobs():

    today = datetime.datetime.now()
    scheduler.start()
    create_jobs(
        name='sync_daily',
        job_id='sync_job',
        trigger=IntervalTrigger(hours=int(application.config['INTERVAL'])),
        next_run_time=datetime.datetime(today.year, today.month, today.day, 23, 59)
    )

    scheduler.print_jobs()
    atexit.register(lambda: scheduler.shutdown())

init()
