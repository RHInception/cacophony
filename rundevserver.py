#!/usr/bin/env python
import os
import sys
sys.path.insert(0, os.path.realpath('src/'))
os.environ['CACOPHONY_CONFIG'] = 'example-settings.json'
from cacophony import app
app.run(debug=True)
