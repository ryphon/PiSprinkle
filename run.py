# -*- encoding: utf-8 -*-

from aiohttp import web
import os
from sprinkler import app
from sprinkler.models import Zone


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    try:
        web.run_app(app, host='0.0.0.0', port=port)
    finally:
        Zone.clean_up_all()
