import logging
import os

from flask import Flask, json

CONFIG_FILE = os.environ.get('CACOPHONY_CONFIG', 'settings.json')

app = Flask(__name__)
app.config.update(json.load(open(CONFIG_FILE, 'r')))

log_handler = logging.FileHandler(app.config.get('LOGFILE', 'cacophony.log'))
log_handler.setLevel(logging.INFO)
log_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))
app.logger.handlers = [log_handler]

import cacophony.views
