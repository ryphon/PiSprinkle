"""
Created on Apr 20, 2018

@author: jusdino
"""
import asyncio
import threading

from apscheduler.schedulers.asyncio import AsyncIOScheduler as APScheduler
from datetime import datetime
from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from sprinkler import app, db
from sprinkler.models import Zone


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
                url=app['APSCHEDULE_DATABASE_URI'])
        }
        self._sched = APScheduler(jobstores=jobstores)

    @classmethod
    def get_uri(cls, job_id: str):
        return str(app.router[cls.endpoint].url_for(id=str(job_id)))

    def add_job(self, *args, **kwargs):
        args, kwargs = self._map_rest_to_apsched(*args, **kwargs)
        app.logger.info(msg=(args, kwargs))
        job = self._sched.add_job(*args, **kwargs)
        return self._map_job_to_dict(job)

    def get_jobs(self) -> list:
        return [self._map_job_to_dict(job) for job in self._sched.get_jobs()]

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
        zone = db.query(Zone).get(zoneID)
        if zone is not None:
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
            raise ValueError('No zone defined with id {}'.format(zoneID))


async def run_zone(zone_id: str, minutes: float):
    app.logger.debug('Job thread: %s', threading.get_ident())
    zone = db.query(Zone).get(zone_id)
    if zone:
        zone.state = 'on'
        # socketio.emit('zone-update',
        #               marshal(zone, sprinkler.views.ZoneAPI.fields))
        await asyncio.sleep(60 * minutes)
        zone.state = 'off'
        # socketio.emit('zone-update',
        #               marshal(zone, sprinkler.views.ZoneAPI.fields))
