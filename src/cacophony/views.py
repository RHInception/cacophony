from flask.views import MethodView
from flask import json, request
from cacophony import app
from cacophony.decorators import remote_user_required

from cacophony.ca import CA

ALL_CAS = {}
app.logger.info("Loading CA's...")
for ca_name in app.config['CA'].keys():
    app.logger.debug('Loading CA %s with: %s' % (
        ca_name, app.config['CA'][ca_name]))
    ALL_CAS[ca_name] = CA(**app.config['CA'][ca_name])
    app.logger.info('Loaded CA="%s"' % ca_name)
app.logger.info("Finished loading %s CA's." % len(ALL_CAS))


def get_auth_decorator():
    """
    Loads and returns the proper auth decorator.
    """
    mod, deco_name = app.config['AUTH_DECORATOR'].split(':')
    app.logger.debug('Loaded AUTH_DECORATOR module="%s", class="%s"' % (
                     mod, deco_name))
    return getattr(__import__(mod, fromlist=['True']), deco_name)


class V1CertificateAPI(MethodView):
    """
    API for certificate creation.
    """
    #: Decorator to be applied to all API methods in this class.
    decorators = [get_auth_decorator()]

    def get(self, environment, hostname):
        """
        The GET request for getting information on a certificate.

        Always returns JSON.

        Returns owner and hostname if found. Otherwise returns an error.
        """
        identifier = "%s/%s" % (request.remote_user, request.remote_addr)
        app.logger.info(
            '%s requested info for %s/%s' % (
                identifier, environment, hostname))
        try:
            cur_ca = ALL_CAS[environment]
            # if the hostname does not exist ...
            cert_list = cur_ca.list_certs()
            if hostname in cert_list.keys():
                return json.dumps({
                    'owner': cert_list[hostname]['_cn_email'],
                    'hostname': hostname,
                }), 200
            app.logger.info(
                "%s request for %s/%s as not found. Unknown host." % (
                identifier, environment, hostname))
            return json.dumps({'error': 'Host not found'}), 404
        except KeyError, ke:
            app.logger.info(
                "%s request for %s/%s as not found. Unknown environment." % (
                identifier, environment, hostname))
            return json.dumps({'error': 'Unknown environment'}), 400

    def put(self, environment, hostname):
        """
        The PUT request for creating new certificates.

        Returns a pem formated response on success, otherswise
        error in JSON format.
        """
        identifier = "%s/%s" % (request.remote_user, request.remote_addr)
        try:
            data = json.loads(request.data)
            email = data['email']
            alt_names = data.get('alt_names', [])
            app.logger.debug(
                'PUT request by %s: environment="%s", '
                'hostname="%s", data="%s".' % (
                    identifier, environment, hostname, data))
            cur_ca = ALL_CAS[environment]
            # if the hostname does not exist ...
            if hostname not in cur_ca.list_certs().keys():
                req, key = cur_ca.create_req(
                    hostname=hostname, emailAddress=email)
                cert = cur_ca.sign_server_cert(
                    req, alt_names=alt_names, format="string")
                if alt_names:
                    app.logger.warn(
                        '%s generated a certificate with alt_names of '
                        '"%s" for %s/%s' % (
                            identifier, alt_names, environment, hostname))
                else:
                    app.logger.info(
                        '%s generated a certificate for %s/%s' % (
                        identifier, environment, hostname))

                return str(key + '\n' + cert), 201
            app.logger.warn(
                '%s tried to create a cert for %s/%s but it already exists' % (
                    identifier, environment, hostname))

            return json.dumps({'error': 'Host already exists'}), 409
        except KeyError, ke:
            return json.dumps({'error': 'Missing ' + str(ke)}), 400


# Routing
cert_api_view = V1CertificateAPI.as_view('cert_api_view')

app.add_url_rule('/api/v1/certificate/<environment>/<hostname>/',
                 view_func=cert_api_view, methods=['GET', ])
app.add_url_rule('/api/v1/certificate/<environment>/<hostname>/',
                 view_func=cert_api_view, methods=['PUT', ])
