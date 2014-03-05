# Copyright (C) 2014 SEE AUTHORS FILE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os

from flask import Flask, json

CONFIG_FILE = os.environ.get('CACOPHONY_CONFIG', 'settings.json')

app = Flask(__name__)
app.config.update(json.load(open(CONFIG_FILE, 'r')))

log_handler = logging.FileHandler(app.config.get('LOGFILE', 'cacophony.log'))
log_level = app.config.get('LOGLEVEL', None)
if not log_level:
    log_level = 'INFO'
log_handler.setLevel(logging.getLevelName(log_level))
log_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))
app.logger.handlers = [log_handler]

import cacophony.views
