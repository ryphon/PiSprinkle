# -*- encoding: utf-8 -*-

from flask import render_template

from sprinkler import app, db, api
from sprinkler.models import Zone
from werkzeug.utils import redirect
from flask.helpers import url_for
from flask_restful import Resource, reqparse, fields, marshal
import sys


class ZoneAPI(Resource):
    ''' REST resource representing irrigation zone '''
    parser = reqparse.RequestParser()
    parser.add_argument('state', type=str, help='Turn the zone on or off')
    parser.add_argument('name', type=str, help='Name of the zone')

    fields = {
        'uri': fields.Url('zone'),
        'state': fields.String,
        'name': fields.String
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
        db.session.add(zone)
        db.session.commit()
        # Reset and query zone to trigger init_on_load
        zone_id = zone.id
        zone = None
        zone = Zone.query.get(zone_id)
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
    return render_template('index.html',
                           zones=Zone.query.all())


@app.route('/view')
def view():
    return render_template('index.html')
