from flask import json

from . import TestCase, unittest


class TestAPIPut(TestCase):

    def test_create_new_cert(self):
        """
        New certificates should be creatable.
        """
        data = json.dumps({'email': 'test@example.com'})
        result = self.client.put(
            '/api/v1/certificate/Test/newhost.example.com/', data=data,
            environ_overrides={'REMOTE_USER': 'testuser'})
        assert result.status_code == 201
        # Verify we did NOT get a json response
        self.assertRaises(ValueError, json.loads, result.data)

        data = json.dumps({
            'email': 'test@example.com',
            'insecure_policy': True,
        })
        result = self.client.put(
            '/api/v1/certificate/Test/insecure.example.com/', data=data,
            environ_overrides={'REMOTE_USER': 'testuser'})
        assert result.status_code == 201
        # Verify we did NOT get a json response
        self.assertRaises(ValueError, json.loads, result.data)

    def test_create_new_cert_fails_on_missing_inputs(self):
        """
        Verify all that are required must be passed to create new certs.
        """
        data = json.dumps({})
        result = self.client.put('/api/v1/certificate/Test/fail.example.com/',
            data=data,
            environ_overrides={'REMOTE_USER': 'testuser'})
        assert result.status_code == 400
        assert 'error' in json.loads(result.data).keys()

    def test_create_new_cert_fails_if_cert_exists(self):
        """
        If a certificate already exists one should be be able to be created.
        """
        data = json.dumps({'email': 'test@example.com'})
        result = self.client.put(
            '/api/v1/certificate/Test/test.example.com/', data=data,
            environ_overrides={'REMOTE_USER': 'testuser'})
        print result
        assert result.status_code == 409
        assert 'error' in json.loads(result.data).keys()

    def test_anon_user_can_not_create_cert(self):
        """
        Anon users can not create certificates.
        """
        data = json.dumps({'email': 'test@example.com'})
        result = self.client.put(
            '/api/v1/certificate/Test/fail.example.com/', data=data)
        assert result.status_code == 401

        result = self.client.put(
            '/api/v1/certificate/Test/fail.example.com/', data=data)
        assert result.status_code == 401

        data = json.dumps({
            'email': 'test@example.com',
            'insecure_policy': True,
        })
        result = self.client.put(
            '/api/v1/certificate/Test/fail.example.com/', data=data)
        assert result.status_code == 401

        data = json.dumps({})
        result = self.client.put(
            '/api/v1/certificate/Test/fail.example.com/', data=data)
        assert result.status_code == 401
