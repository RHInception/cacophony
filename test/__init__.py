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

import os

from flask import json

os.environ['CACOPHONY_CONFIG'] = 'example-settings.json'

from cacophony import app

import unittest


with open('test/Test-CA/index.txt', 'w') as index_f:
    index_f.write('V	20150220193307Z		10	unknown	/CN=test.example.com/emailAddress=me@example.com\n')


class TestCase(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
