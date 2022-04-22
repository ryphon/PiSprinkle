# -*- encoding: utf-8 -*-

from flask import render_template

from sprinkler import app, db, api, sched
from sprinkler.models import Zone
from werkzeug.utils import redirect
from flask.helpers import url_for
from flask_restful import Resource, reqparse, fields, marshal
from sqlalchemy.exc import IntegrityError
import sys
from flask.globals import request


class ZoneAPI(Resource):
    ''' REST resource representing irrigation zone '''
    parser = reqparse.RequestParser()
    parser.add_argument('state', type=str, help='Turn the zone on or off')
    parser.add_argument('name', type=str, help='Name of the zone')

    fields = {
        'uri': fields.Url('zone'),
        'id': fields.Integer,
        'name': fields.String,
        'state': fields.String,
        'pin': fields.Integer
        }

    def get(self, id: int):
        zone = Zone.query.get(id)
        if zone:
            return marshal(zone, ZoneAPI.fields)

    def put(self, id: int):
        zone = Zone.query.get(id)
        if zone:
            args = self.parser.parse_args(strict=True)
            if args.get('state') is not None:
                zone.state = args['state']
            if args.get('name') is not None:
                zone.name = args['name']
                db.session.commit()
            return marshal(zone, ZoneAPI.fields)

    def delete(self, id):
        zone = Zone.query.get(id)
        if zone:
            db.session.delete(zone)
            db.session.commit()
        return ''


class ZoneListAPI(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('state',
                        type=bool,
                        help='Turn the zone on or off')
    parser.add_argument('name',
                        type=str,
                        help='Name of the zone',
                        required=True)
    parser.add_argument('pin',
                        type=int,
                        help='Pin number controlling zone',
                        required=True)

    def get(self):
        return marshal(Zone.query.all(), ZoneAPI.fields)

    def post(self):
        args = self.parser.parse_args(strict=True)
        zone = Zone(name=args['name'],
                    pin=args['pin'])
        try:
            db.session.add(zone)
            db.session.commit()
        except IntegrityError:
            app.logger.warning(
                'Invalid zone creation attempted: {}'.format(zone))
            zone.clean_up()
            app.logger.warning('Failed to create zone {}'.format(zone), file=sys.stderr)
            return {'message': 'Failed to create zone'}, 400
        if args.get('state') is not None:
            zone.state = args['state']
        return marshal(zone, ZoneAPI.fields)


class ScheduleAPI(Resource):

    fields = {
        'uri': fields.Url('schedule'),
        'id': fields.String,
        'zoneID': fields.Integer,
        'minutes': fields.Float,
        'day_of_week': fields.String,
        'hour': fields.String,
        'minute': fields.String,
        'second': fields.String
        }

    def get(self, id: str):
        try:
            return marshal(sched.get_job(id), ScheduleAPI.fields)
        except ValueError as exc:
            app.logger.warn(str(exc))
            return {"message": str(exc)}, 400

#    Not worth implementing
#     def put(self, id: str):
#         args = self.parser.parse_args(strict=True)
#         try:
#             return sched.modify_job(id, **args)
#         except (ValueError, AttributeError, JobLookupError) as exc:
#             return {'message': str(exc)}, 400

    def delete(self, id: str):
        try:
            sched.remove_job(id)
            return ''
        except ValueError as exc:
            return {'message': str(exc)}, 400


class ScheduleListAPI(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('zoneID',
                        type=int,
                        help='ID number for zone',
                        required=True)
    parser.add_argument('minutes',
                        type=float,
                        help='Minutes to run zone for',
                        required=True)
    parser.add_argument('day_of_week',
                        type=list,
                        location='json',
                        help='Weekdays to run zone')
    parser.add_argument('hour',
                        type=str,
                        help='Hour to start on',
                        required=True)
    parser.add_argument('minute',
                        type=str,
                        help='Minute to start on')
    parser.add_argument('second',
                        type=str,
                        help='Second to start on')

    def get(self):
        return marshal(sched.get_jobs(), ScheduleAPI.fields)

    def post(self):
        app.logger.info(request.json)
        args = self.parser.parse_args(strict=True)
        app.logger.info(args)
        try:
            return marshal(sched.add_job(**args), ScheduleAPI.fields)
        except ValueError as exc:
            app.logger.warn(str(exc))
            return {'message': str(exc)}, 400


api.add_resource(ZoneAPI,
                 '/zones/<int:id>',
                 endpoint='zone')
api.add_resource(ZoneListAPI,
                 '/zones',
                 endpoint='zones')
api.add_resource(ScheduleAPI,
                 '/schedules/<id>',
                 endpoint='schedule')
api.add_resource(ScheduleListAPI,
                 '/schedules',
                 endpoint='schedules')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/view')
def view():
    return redirect(url_for('index'))
