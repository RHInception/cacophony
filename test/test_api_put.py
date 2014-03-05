import OpenSSL.crypto

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
        # Verify there are NO alt names
        with open(
                'test/Test-CA/certs/by-name/newhost.example.com.crt') as crt:
            certificate = OpenSSL.crypto.load_certificate(
                OpenSSL.crypto.FILETYPE_PEM,
                crt.read())
            for x in range(0, certificate.get_extension_count()):
                self.assertNotEquals(
                    'subjectAltName',
                    certificate.get_extension(x).get_short_name())

        data = json.dumps({
            'email': 'test@example.com',
            'alt_names': ['multi1.example.com', 'multi2.example.com'],
        })
        result = self.client.put(
            '/api/v1/certificate/Test/multi.example.com/', data=data,
            environ_overrides={'REMOTE_USER': 'testuser'})
        assert result.status_code == 201
        # Verify we did NOT get a json response
        self.assertRaises(ValueError, json.loads, result.data)
        # Verify the resulting certificate has altnames
        found_alt_names = False
        with open(
                'test/Test-CA/certs/by-name/multi.example.com.crt') as crt:
            certificate = OpenSSL.crypto.load_certificate(
                OpenSSL.crypto.FILETYPE_PEM,
                crt.read())
            for x in range(0, certificate.get_extension_count()):
                if 'subjectAltName' == certificate.get_extension(
                        x).get_short_name():
                    found_alt_names = True
                    assert 'multi1.example.com' in certificate.get_extension(
                        x).get_data()
                    assert 'multi2.example.com' in certificate.get_extension(
                        x).get_data()

        assert found_alt_names

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
            'alt_names': ['multi1.example.com', 'multi2.example.com'],
        })

        result = self.client.put(
            '/api/v1/certificate/Test/fail.example.com/', data=data)
        assert result.status_code == 401

        data = json.dumps({})
        result = self.client.put(
            '/api/v1/certificate/Test/fail.example.com/', data=data)
        assert result.status_code == 401
