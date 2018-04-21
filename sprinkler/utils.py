#!/bin/python
from sprinkler.models import Zone
import time

# zoneNums = [4, 10, 27, 22, 5, 6]


def run_zone(zoneID: int, minutes: float):
    zone = Zone.query.get(zoneID)
    if zone:
        zone.state = 'on'
        time.sleep(60*minutes)
        zone.state = 'off'
