# -*- encoding: utf-8 -*-

import os
from sprinkler import app, sched
from sprinkler.models import Zone


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    try:
        app.run(host='0.0.0.0', port=port)
    finally:
        sched.pause()
        Zone.clean_up_all()
