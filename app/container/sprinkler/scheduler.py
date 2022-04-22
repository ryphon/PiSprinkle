"""
Created on Apr 20, 2018

@author: jusdino
<<<<<<<< HEAD:app/container/sprinkler/schedule.py
'''
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sprinkler import app
import sprinkler
import time
========
"""
import asyncio
import threading

from apscheduler.schedulers.asyncio import AsyncIOScheduler as APScheduler
from datetime import datetime
from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from sprinkler import app, db
from sprinkler.models import Zone
>>>>>>>> 3ff41277525901f24c0329937b5298c5799b9531:app/container/sprinkler/scheduler.py


class Scheduler(object):
    """
    Handler class for communicating with apscheduler BackgroundScheduler
    """

    CRON_FIELDS = ('day_of_week', 'hour', 'minute', 'second')
    WEEKDAYS = {
        0: 'mon',
        1: 'tue',
        2: 'wed',
        3: 'thu',
        4: 'fri',
        5: 'sat',
        6: 'sun'}
    endpoint = 'schedule'

    def __init__(self):
        jobstores = {
            'default': SQLAlchemyJobStore(
<<<<<<<< HEAD:app/container/sprinkler/schedule.py
                url=app.config['APSCHEDULE_DATABASE_URI'])
        }
        self._sched = BackgroundScheduler(jobstores=jobstores)
========
                url=app['APSCHEDULE_DATABASE_URI'])
            }
        self._sched = APScheduler(jobstores=jobstores)

    @classmethod
    def get_uri(cls, job_id: str):
        return str(app.router[cls.endpoint].url_for(id=str(job_id)))
>>>>>>>> 3ff41277525901f24c0329937b5298c5799b9531:app/container/sprinkler/scheduler.py

    def add_job(self, *args, **kwargs):
        args, kwargs = self._map_rest_to_apsched(*args, **kwargs)
        app.logger.info(msg=(args, kwargs))
        job = self._sched.add_job(*args, **kwargs)
        return self._map_job_to_dict(job)

<<<<<<<< HEAD:app/container/sprinkler/schedule.py
#    Just add/delete jobs. Not worth modifying - especially since modifying
#    triggers is a whole different thing.
#     def modify_job(self, jobID: str, *args, **kwargs):
#         args, kwargs = self._map_rest_to_apsched(*args, **kwargs)
#         job = self._sched.modify_job(jobID, **kwargs)
#         return self._map_job_to_dict(job)

    def get_jobs(self) -> list:
        jobs = []
        for job in self._sched.get_jobs():
            jobs.append(self._map_job_to_dict(job))
        return jobs
========
    def get_jobs(self) -> list:
        return [self._map_job_to_dict(job) for job in self._sched.get_jobs()]
>>>>>>>> 3ff41277525901f24c0329937b5298c5799b9531:app/container/sprinkler/scheduler.py

    def get_job(self, jobID: str):
        return self._map_job_to_dict(self._sched.get_job(jobID))

    def pause(self):
        self._sched.pause()

    def remove_job(self, jobID: str):
        self._sched.remove_job(jobID)

    def remove_jobs_for_zone(self, zoneID: int):
        jobs = self.get_jobs()
        for job in jobs:
            if job['zoneID'] == zoneID:
                self.remove_job(job['id'])

    def start(self):
        self._sched.start()

    def shutdown(self):
        self._sched.shutdown()

    @classmethod
    def _map_job_to_dict(cls, job: Job):
        # TODO: add start_date, end_date
        dict_job = {
            'uri': cls.get_uri(job.id),
            'id': job.id,
            'zoneID': job.args[0],
            'minutes': job.args[1]
        }
        for field in job.trigger.fields:
            if field.name in cls.CRON_FIELDS:
                dict_job[field.name] = str(field)
        return dict_job

    @classmethod
    def _map_rest_to_apsched(cls,
                             zoneID: int,
                             minutes: float,
                             start: datetime = None,
                             end: datetime = None,
                             **kwargs):
<<<<<<<< HEAD:app/container/sprinkler/schedule.py
        if sprinkler.models.Zone.query.get(zoneID) is not None:
========
        zone = db.query(Zone).get(zoneID)
        if zone is not None:
>>>>>>>> 3ff41277525901f24c0329937b5298c5799b9531:app/container/sprinkler/scheduler.py
            cronFields = {}
            for key, value in kwargs.items():
                if key in cls.CRON_FIELDS:
                    cronFields[key] = value
            args = (run_zone, 'cron')
            kwargs = cronFields
            # Change day_of_week numbers to name abbrs
            # and join into a string
            if kwargs.get('day_of_week') is not None:
                dow = kwargs['day_of_week']
                kwargs['day_of_week'] = \
                    ','.join([cls.WEEKDAYS[x]
                              if x in cls.WEEKDAYS.keys()
                              else x
                              for x in dow])
            kwargs['start_date'] = start
            kwargs['end_date'] = end
            kwargs['args'] = [zoneID, minutes]
            return args, kwargs
        else:
<<<<<<<< HEAD:app/container/sprinkler/schedule.py
            raise KeyError('No zone defined with id {}'.format(zoneID))


def run_zone(zoneID: int, minutes: float):
    zone = sprinkler.models.Zone.query.get(zoneID)
    if zone:
        zone.state = 'on'
        time.sleep(60 * minutes)
        zone.state = 'off'
========
            raise ValueError('No zone defined with id {}'.format(zoneID))


async def run_zone(zone_id: str, minutes: float):
    app.logger.debug('Job thread: %s', threading.get_ident())
    zone = db.query(Zone).get(zone_id)
    if zone:
        zone.state = 'on'
        # socketio.emit('zone-update',
        #               marshal(zone, sprinkler.views.ZoneAPI.fields))
        await asyncio.sleep(60*minutes)
        zone.state = 'off'
        # socketio.emit('zone-update',
        #               marshal(zone, sprinkler.views.ZoneAPI.fields))
>>>>>>>> 3ff41277525901f24c0329937b5298c5799b9531:app/container/sprinkler/scheduler.py
