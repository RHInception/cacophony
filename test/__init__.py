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
