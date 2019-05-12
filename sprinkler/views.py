# -*- encoding: utf-8 -*-
import functools

from aiohttp import web
from sqlalchemy.exc import IntegrityError

from sprinkler import app, db, sched, aj
from sprinkler.models import Zone


def check_args(fn):
    @functools.wraps(fn)
    async def wrapper(slf: BaseWebView):
        # Mash together request json, query args, url args
        args = await slf.request.json()
        args.update(slf.request.query)
        args.update(slf.request.match_info)
        for req_arg in slf.REQUIRED_ARGS:
            try:
                arg = args[req_arg['name']]
            except KeyError:
                return web.json_response(
                    {'message': 'Missing required argument: {} ({})'.format(
                        req_arg["name"], req_arg["help"]
                    )},
                    status=400)
            # Cast arg to required type
            try:
                args[req_arg['name']] = req_arg['type'](arg)
            except TypeError:
                return web.json_response(
                    {'message': '{} must be of type {}'.format(
                        req_arg["name"], req_arg["type"]
                    )},
                    status=406)
        slf.request.mashed_args = args
        return await fn(slf)
    return wrapper


class BaseWebView(web.View):
    REQUIRED_ARGS = []


class ZoneAPI(BaseWebView):
    """ REST resource representing irrigation zone """
    REQUIRED_ARGS = [
        {
            'name': 'state',
            'type': str,
            'help': 'Turn the zone on or off'
        }
    ]

    # parser = reqparse.RequestParser()
    # parser.add_argument('state', type=str, help='Turn the zone on or off')
    # parser.add_argument('name', type=str, help='Name of the zone')

    async def get(self):
        id = self.request.match_info['id']
        zone = db.query(Zone).get(id)
        if zone:
            return web.json_response(zone.as_dict)

    @check_args
    async def put(self):
        id = self.request.match_info['id']
        zone = db.query(Zone).get(id)
        if zone:
            # args = self.parser.parse_args(strict=True)
            args = self.request.mashed_args
            if args.get('state') is not None:
                zone.state = args['state']
            if args.get('name') is not None:
                zone.name = str(args['name'])
                db.commit()
            return web.json_response(zone.as_dict)

    async def delete(self):
        id = self.request.match_info['id']
        zone = db.query(Zone).get(id)
        if zone:
            db.delete(zone)
            db.commit()
        return web.Response(text='')


class ZoneListAPI(BaseWebView):
    REQUIRED_ARGS = [
        {
            'name': 'name',
            'type': str,
            'help': 'Name of the zone'
        },
        {
            'name': 'pin',
            'type': int,
            'help': 'BCM pin number controlling the zone'
        }
    ]
    # parser = reqparse.RequestParser()
    # parser.add_argument('state',
    #                     type=bool,
    #                     help='Turn the zone on or off')
    # parser.add_argument('name',
    #                     type=str,
    #                     help='Name of the zone',
    #                     required=True)
    # parser.add_argument('pin',
    #                     type=int,
    #                     help='Pin number controlling zone',
    #                     required=True)

    async def get(self):
        return web.json_response(tuple(zone.as_dict for zone in db.query(Zone).all()))

    @check_args
    async def post(self):
        # args = self.parser.parse_args(strict=True)
        args = self.request.mashed_args
        zone = Zone(name=args['name'],
                    pin=args['pin'])
        try:
            db.add(zone)
            db.commit()
        except IntegrityError:
            app.logger.warning(
                'Invalid zone creation attempted: {}'.format(zone))
            zone.clean_up()
            app.logger.warning('Failed to create zone {}'.format(zone))
            return web.json_response({'message': 'Failed to create zone'}, status=400)
        if args.get('state') is not None:
            zone.state = args['state']
        if not hasattr(zone, 'id') or zone.id is None:
            app.logger.warn('New created zone was not given an id: {}'
                            .format(zone.name))
            db.flush()
            zone = db.query(Zone).filter_by(name=zone.name)
        return web.json_response(zone.as_dict)


class ScheduleAPI(BaseWebView):

    async def get(self):
        id = self.request.match_info['id']
        try:
            return web.json_response(sched.get_job(id))
        except ValueError as exc:
            app.logger.warn(str(exc))
            return web.json_response({"message": str(exc)}, status=400)

    async def delete(self):
        id = self.request.match_info['id']
        try:
            sched.remove_job(id)
            return web.Response(text='')
        except ValueError as exc:
            return web.json_response({'message': str(exc)}, status=400)


class ScheduleListAPI(BaseWebView):
    REQUIRED_ARGS = [
        {
            'name': 'zoneID',
            'type': int,
            'help': 'ID number for zone'
        },
        {
            'name': 'minutes',
            'type': float,
            'help': 'Minutes to run zone for'
        },
        {
            'name': 'day_of_week',
            'type': list,
            'help': 'Weekdays to run zone'
        },
        {
            'name': 'hour',
            'type': str,
            'help': 'Hour to start on'
        },
        {
            'name': 'minute',
            'type': str,
            'help': 'Minute to start on'
        },
        {
            'name': 'second',
            'type': str,
            'help': 'Second to start on'
        }

    ]
    # parser = reqparse.RequestParser()
    # parser.add_argument('zoneID',
    #                     type=int,
    #                     help='ID number for zone',
    #                     required=True)
    # parser.add_argument('minutes',
    #                     type=float,
    #                     help='Minutes to run zone for',
    #                     required=True)
    # parser.add_argument('day_of_week',
    #                     type=list,
    #                     location='json',
    #                     help='Weekdays to run zone')
    # parser.add_argument('hour',
    #                     type=str,
    #                     help='Hour to start on',
    #                     required=True)
    # parser.add_argument('minute',
    #                     type=str,
    #                     help='Minute to start on')
    # parser.add_argument('second',
    #                     type=str,
    #                     help='Second to start on')

    async def get(self):
        return web.json_response(sched.get_jobs())

    @check_args
    async def post(self):
        app.logger.info(self.request.json)
        # args = self.parser.parse_args(strict=True)
        args = self.request.mashed_args
        app.logger.info(args)
        try:
            return web.json_response(sched.add_job(**args))
        except ValueError as exc:
            app.logger.warn(str(exc))
            return web.json_response({'message': str(exc)}, status=400)


@aj.template('index.html')
async def index(request):
    return {}


app.router.add_view('/zones/{id:\d+}', ZoneAPI, name='zone')
app.router.add_view('/zones', ZoneListAPI, name='zones')
app.router.add_view('/schedules/{id:\d+}', ScheduleAPI, name='schedule')
app.router.add_view('/schedules', ScheduleListAPI, name='schedules')
app.router.add_route('GET', '/', index)
