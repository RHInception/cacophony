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

import csv
import os

from OpenSSL import crypto


class CA(object):
    '''
    This class implements a basic CA that can create requests and sign
    certificates.  It can output in pyOpenSSL formats with 'format="obejct"'
    but by default outputs in PEM format.

    It expects certs/requests/keys in PEM format'''

    def __init__(self, pubCert=None, privKey=None, privPass=None,
                 serial="CA/serial", index="CA/index.txt",
                 certStore='CA/certs/by-name',
                 reqStore='CA/requests/', keySize=4096,
                 validTime=60 * 60 * 24 * 365):

        self.privKey = crypto.load_privatekey(
            crypto.FILETYPE_PEM, open(privKey, "r").read(), str(privPass))
        self.pubCert = crypto.load_certificate(
            crypto.FILETYPE_PEM, open(pubCert, "r").read())

        self.serialFile = os.path.realpath(serial)
        self.serial = int(open(self.serialFile, "r").read(), 16)
        self.validTime = validTime
        self.keySize = keySize
        self.index = os.path.realpath(index)
        self.certStore = os.path.realpath(certStore)
        self.reqStore = os.path.realpath(reqStore)

    def sign_server_cert(self, certRequest, alt_names=[], format="string"):
        # given a CSR (PEM-encoded "string" or X509Req "object")
        # sign and return an X509 cert object
        newcert = crypto.X509()

        # Check the format, return None if it's not a valid format
        if format == "string":
            req = crypto.load_certificate_request(
                crypto.FILETYPE_PEM, certRequest)
        elif format == "object":
            req = certRequest
        else:
            return None

        newcert.set_version(3)
        # Get the current serial
        self.serial = int(open(self.serialFile, "r").read(), 16)
        newcert.set_serial_number(self.serial)
        newcert.set_subject(req.get_subject())
        newcert.gmtime_adj_notBefore(0)
        newcert.gmtime_adj_notAfter(self.validTime)
        newcert.set_issuer(self.pubCert.get_subject())
        newcert.set_pubkey(req.get_pubkey())
        # Basic x509 extensions for a server cert
        extensions = [
            # Not a CA
            crypto.X509Extension("basicConstraints", True, "CA:FALSE"),
            # What you can use the key for
            crypto.X509Extension(
                "keyUsage", False,
                "nonRepudiation, digitalSignature, keyEncipherment"),
            # How to ID the subject
            crypto.X509Extension("subjectKeyIdentifier", False,
                                 "hash", subject=newcert),
            # How to ID the issuer
            crypto.X509Extension("authorityKeyIdentifier", False,
                                 "keyid:always", issuer=self.pubCert),
            # "type" of cert
            crypto.X509Extension("extendedKeyUsage", False, "serverAuth")
        ]

        if alt_names:
            alt_str = ""
            for alt in alt_names:
                alt_str += "DNS:" + alt + ", "
            alt_str = alt_str[:-2]
            extensions.append(crypto.X509Extension(
                "subjectAltName", False, alt_str))
        newcert.add_extensions(extensions)

        newcert.sign(self.privKey, "sha256")

        # Get the CN and set it as the hostname for the output file
        for key, val in newcert.get_subject().get_components():
            if key == 'CN':
                hostname = val

        # Update the serial and index.txt
        with open(self.serialFile, "w") as serialfile:
            serialfile.write('%x' % (self.serial + 1))

        with open(self.index, "a") as indexfile:
            name = ""
            for item in newcert.get_subject().get_components():
                name = name + "/%s=%s" % (item[0], item[1])

            indexfile.write('V\t%s\t\t%x\tunknown\t%s\n' % (
                newcert.get_notAfter(), self.serial, name))

        cert_str = crypto.dump_certificate(crypto.FILETYPE_PEM, newcert)
        with open(os.path.sep.join([
                  self.certStore, hostname + '.crt']), 'w') as cert_file:
            cert_file.write(cert_str)

        if format == "string":
            return cert_str
        else:
            return newcert

    def create_req(self, hostname, emailAddress, format="string"):
        # given a hostname and email, generate and sign a certificate,
        # return the cert + key
        req = crypto.X509Req()
        keys = crypto.PKey()
        keys.generate_key(crypto.TYPE_RSA, self.keySize)

        req.set_pubkey(keys)
        req.get_subject().CN = hostname
        req.get_subject().emailAddress = emailAddress
        req.sign(keys, "sha256")

        req_str = crypto.dump_certificate_request(crypto.FILETYPE_PEM, req)
        key_str = crypto.dump_privatekey(crypto.FILETYPE_PEM, keys)

        with open(os.path.sep.join([
                  self.reqStore, hostname + '.req']), 'w') as req_file:
            req_file.write(req_str)

        if format == "string":
            return (req_str, key_str)
        else:
            return req, keys

    def list_certs(self):
        """
        Returns a data structure of all registered certs.
        """
        results = {}
        reader = csv.DictReader(
            open(self.index, 'r'),
            fieldnames=['Status', 'Valid Until', 'Date Revoked',
                        'Serial', 'Filename', 'SubjectDN'],
            dialect=csv.excel_tab)

        for item in reader:
            for sub_item in item['SubjectDN'].split('/'):
                data = sub_item.split('=')
                if len(data) == 2:
                    key = data[0].lower()
                    if key == 'cn':
                        item['_cn_hostname'] = data[1]
                    elif key == 'emailaddress':
                        item['_cn_email'] = data[1]
                    else:
                        item['_cn_%s' % (key)] = data[1]
            results[item['_cn_hostname']] = item
        return results
