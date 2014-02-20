import os

from flask import Flask, json

CONFIG_FILE = os.environ.get('CACOPHONY_CONFIG', 'settings.json')

app = Flask(__name__)
app.config.update(json.load(open(CONFIG_FILE, 'r')))

import cacophony.views
