from flask.views import MethodView
from flask import json, request
from cacophony import app
from cacophony.decorators import remote_user_required

from cacophony.ca import CA

ALL_CAS = {}
for ca_name in app.config['CA'].keys():
    ALL_CAS[ca_name] = CA(**app.config['CA'][ca_name])


def get_auth_decorator():
    mod, deco_name = app.config['AUTH_DECORATOR'].split(':')
    return getattr(__import__(mod, fromlist=['True']), deco_name)


class CertificateAPI(MethodView):

    decorators = [get_auth_decorator()]

    def get(self, environment, hostname):
        app.logger.info(
            '%s requested info for %s/%s' % (
                request.remote_user, environment, hostname))
        try:
            cur_ca = ALL_CAS[environment]
            # if the hostname does not exist ...
            cert_list = cur_ca.list_certs()
            if hostname in cert_list.keys():
                return json.dumps({
                    'owner': cert_list[hostname]['_cn_email'],
                    'hostname': hostname,
                }), 200
            return json.dumps({'error': 'Host not found'}), 404
        except KeyError, ke:
            return json.dumps({'error': 'Unknown environment'}), 400

    def put(self, environment, hostname):
        try:
            data = json.loads(request.data)
            email = data['email']
            insecure_policy = bool(data.get('insecure_policy', False))
            cur_ca = ALL_CAS[environment]
            # if the hostname does not exist ...
            if hostname not in cur_ca.list_certs().keys():
                if insecure_policy:
                    app.logger.info(
                        '%s generated an insecure certificate for %s' % (
                            request.remote_user, hostname))
                req, keys = cur_ca.create_req(
                    hostname=hostname, emailAddress=email)
                cert = cur_ca.sign_server_cert(req, format="string")
                return str(cert), 201
            return json.dumps({'error': 'Host already exists'}), 409
        except KeyError, ke:
            return json.dumps({'error': 'Missing ' + str(ke)}), 400


# Routing
cert_api_view = CertificateAPI.as_view('cert_api_view')

app.add_url_rule('/api/v1/certificate/<environment>/<hostname>/',
                 view_func=cert_api_view, methods=['GET', ])
app.add_url_rule('/api/v1/certificate/<environment>/<hostname>/',
                 view_func=cert_api_view, methods=['PUT', ])
