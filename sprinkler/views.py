# -*- encoding: utf-8 -*-

from flask import render_template

from sprinkler import app, db, api
from sprinkler.models import Zone
from werkzeug.utils import redirect
from flask.helpers import url_for
from flask_restful import Resource, reqparse, fields, marshal
from sqlalchemy.exc import IntegrityError


class ZoneAPI(Resource):
    ''' REST resource representing irrigation zone '''
    parser = reqparse.RequestParser()
    parser.add_argument('state', type=str, help='Turn the zone on or off')
    parser.add_argument('name', type=str, help='Name of the zone')

    fields = {
        'uri': fields.Url('zone'),
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
            return {'message': 'Failed to create zone'}, 400
        if args.get('state') is not None:
            zone.state = args['state']
        return marshal(zone, ZoneAPI.fields)


api.add_resource(ZoneAPI,
                 '/zones/<int:id>',
                 endpoint='zone')
api.add_resource(ZoneListAPI,
                 '/zones',
                 endpoint='zones')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/view')
def view():
    return redirect(url_for('index'))
