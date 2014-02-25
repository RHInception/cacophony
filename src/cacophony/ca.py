#!/usr/bin/env python
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
                 serial="CA/serial", index="CA/index.txt", keySize=4096,
                 validTime=60 * 60 * 24 * 365):

        self.privKey = crypto.load_privatekey(
            crypto.FILETYPE_PEM, open(privKey, "r").read(), privPass)
        self.pubCert = crypto.load_certificate(
            crypto.FILETYPE_PEM, open(pubCert, "r").read())

        self.serialFile = os.path.realpath(serial)
        self.serial = int(open(self.serialFile, "r").read(), 16)
        self.validTime = validTime
        self.keySize = keySize
        self.index = os.path.realpath(index)

    def sign_server_cert(self, certRequest, format="string"):
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
        newcert.add_extensions([
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
        ])

        newcert.sign(self.privKey, "sha256")

        # Update the serial and index.txt
        with open(self.serialFile, "w") as serialfile:
            serialfile.write('%x' % (self.serial + 1))

        with open(self.index, "a") as indexfile:
            name = ""
            for item in newcert.get_subject().get_components():
                name = name + "/%s=%s" % (item[0], item[1])

            indexfile.write('V\t%s\t\t%x\tunknown\t%s\n' % (
                newcert.get_notAfter(), self.serial, name))

        if format == "string":
            return crypto.dump_certificate(crypto.FILETYPE_PEM, newcert)
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

        if format == "string":
            return (
                crypto.dump_certificate_request(crypto.FILETYPE_PEM, req),
                crypto.dump_privatekey(crypto.FILETYPE_PEM, keys))
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
