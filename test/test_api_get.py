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

from flask import json

from . import TestCase, unittest


class TestAPIGet(TestCase):

    def test_get_info_on_cert(self):
        """
        Known certificates should return metadata upon request.
        """
        result = self.client.get(
            '/api/v1/certificate/Test/test.example.com/',
            environ_overrides={'REMOTE_USER': 'testuser'})
        assert result.status_code == 200

        keys = json.loads(result.data).keys()
        assert 'owner' in keys
        assert 'hostname' in keys

    def test_get_info_on_unknown_cert(self):
        """
        Unknown certificate request should return an error and 404.
        """
        result = self.client.get(
            '/api/v1/certificate/Test/testdoesnotexist/',
            environ_overrides={'REMOTE_USER': 'testuser'})
        assert result.status_code == 404

        keys = json.loads(result.data).keys()
        assert 'error' in keys

    def test_get_info_on_cert_by_anon_fails(self):
        """
        Anon users can not get any information on certificates.
        """
        result = self.client.get(
            '/api/v1/certificate/Test/test.example.com/')
        assert result.status_code == 401

        result = self.client.get(
            '/api/v1/certificate/Test/testdoesnotexist/')
        assert result.status_code == 401
