#!/usr/bin/python3
# -*- encoding: utf-8 -*-

from aiohttp import web
import os
from sprinkler import app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    web.run_app(app, host='0.0.0.0', port=port)
