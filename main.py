import logging
import json

from process_tracker.processTracker import ProcessTracker
from site_tracker.siteTracker import SiteTracker
from wait_tracker.waitTracker import WaitTracker

with open("config.json", "r") as f:
    config = json.load(f)

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(filename)s %(levelname)-8s %(message)s')

WaitTracker(allow_time=config['allow_time']).run()
ProcessTracker().run()
SiteTracker().run()