'''
Created on Apr 20, 2018

@author: jusdino
'''
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sprinkler import app
import sprinkler
import time


class Scheduler(object):
    '''
    Handler class for communicating with apscheduler BackgroundScheduler
    '''

    CRON_FIELDS = ('day_of_week', 'hour', 'minute', 'second')
    WEEKDAYS = {
        0: 'mon',
        1: 'tue',
        2: 'wed',
        3: 'thu',
        4: 'fri',
        5: 'sat',
        6: 'sun'}

    def __init__(self):
        jobstores = {
            'default': SQLAlchemyJobStore(
                url=app.config['APSCHEDULE_DATABASE_URI'])
        }
        self._sched = BackgroundScheduler(jobstores=jobstores)

    def add_job(self, *args, **kwargs):
        args, kwargs = self._map_rest_to_apsched(*args, **kwargs)
        app.logger.info(msg=(args, kwargs))
        job = self._sched.add_job(*args, **kwargs)
        return self._map_job_to_dict(job)

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

    @classmethod
    def _map_job_to_dict(cls, job: Job):
        # TODO: add start_date, end_date
        dictJob = {}
        dictJob['id'] = job.id
        dictJob['zoneID'] = job.args[0]
        dictJob['minutes'] = job.args[1]
        for field in job.trigger.fields:
            if field.name in cls.CRON_FIELDS:
                dictJob[field.name] = str(field)
        return dictJob

    @classmethod
    def _map_rest_to_apsched(cls,
                             zoneID: int,
                             minutes: float,
                             start: datetime = None,
                             end: datetime = None,
                             **kwargs):
        if sprinkler.models.Zone.query.get(zoneID) is not None:
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
            raise KeyError('No zone defined with id {}'.format(zoneID))


def run_zone(zoneID: int, minutes: float):
    zone = sprinkler.models.Zone.query.get(zoneID)
    if zone:
        zone.state = 'on'
        time.sleep(60 * minutes)
        zone.state = 'off'
