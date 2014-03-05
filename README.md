# cacophony
Simple REST Api for automagic SSL certificate generation.


## Unittests
Use *nosetests -v --with-cover --cover-package cacophony test/* from the main directory to execute unittests. This will use the test/Test-CA/ CA.

## Configuration
Configuration of the server is done in JSON and is by default kept in the current directories settings.json file.

You can override the location by setting `CACOPHONY_CONFIG` environment variable.

| Name            | Type | Parent        | Value                                                               |
|-----------------|------|---------------|---------------------------------------------------------------------|
| AUTH\_DECORATOR | str  | None          | cacophony.decorators:remote\_user\_required (module.name:decorator) |
| LOGFILE         | str  | None          | File name for the application level log                             |
| LOGLEVEL        | str  | None          | Log level to use (DEBUG, INFO, WARN, FATAL). Unset defaults to INFO |
| CA              | dict | None          | A dictionary holding CA configuration data                          |
| "ENVIRONMENT"   | dict | CA            | Configuration info for the CA to be used in "ENVIRONMENT"           |
| privKey         | str  | "ENVIRONMENT" | Path to the CA's private key.                                       |
| privPass        | str  | "ENVIRONMENT" | Password for CA.                                                    |
| pubCert         | str  | "ENVIRONMENT" | Path to the public cert.                                            |
| serial          | str  | "ENVIRONMENT" | Path to the CA's serial file.                                       |
| index           | str  | "ENVIRONMENT" | Path to the CA's index file.                                        |
| keySize         | int  | "ENVIRONMENT" | Key size to use                                                     |
| validTime       | int  | "ENVIRONMENT" | Length of time the certificates will be valid for.                  |
| certStore       | str  | "ENVIRONMENT" | Path to write out certificates after generation.                    |
| reqStore        | str  | "ENVIRONMENT" | Path to write out requests after generation.                        |


### Example Config
```json
{
    "DEBUG": false,
    "PREFERRED_URL_SCHEME": "https",
    "LOGGER_NAME": "cacophony",
    "AUTH_DECORATOR": "cacophony.decorators:remote_user_required",
    "CA": {        
        "Test": { 
            "privKey": "test/Test-CA/private/cakey.pem",
            "privPass": "test",
            "pubCert": "test/Test-CA/cacert.pem",
            "serial": "test/Test-CA/serial",
            "index": "test/Test-CA/index.txt",
            "keySize": 4096,
            "validTime":  31536000,
            "certStore": "test/Test-CA/certs/by-name/",
            "reqStore": "test/Test-CA/requests/"
        }
    }
}
```

Further configuration items can be found at http://flask.pocoo.org/docs/config/#builtin-configuration-values

## Authentication
cacophony uses a simple decorater system for authentication.

### cacophony.decorators:remote\_user\_required
This decorator assumes that cacophony is running behind another web server which is taking care of authentication. If REMOTE\_USER is passed to cacophony from the web server cacophony assumes authentication has succeeded. If it is not passed through cacophony treats the users as unauthenticated.

**WARNING**: When using this decorator it is very important that cacophony not be reachable by any means other than through the front end webserver!!


## URLs
### /api/v2/certificate/*$ENVIRONMENT*/*$HOSTNAME*/

#### GET
*Response Type*: json
*Auth Required*: Yes
*Input Format*: None
*Inputs*: None


#### PUT
*Response Type*: json on error, text pem on cert creation
*Auth Required*: Yes
*Input Format*: json
*Inputs*:
| Name       | Type | Description                           | Example                                     |
| :--------: | :--: | :-----------------------------------: | :-----------------------------------------: |
| email      | str  | Email of the owner                    | owner@example.com                           |
| alt\_names | list | List of other domains the cert is for | ['test.example.com', 'another.example.com'] |

## Deployment

*Note*: However you deploy cacophony make sure the application server can read and write to the files listed in the CA section. If the appserver can not read or write to the files errors will occur.

### Apache with mod\_wsgi
mod_wsgi can be used with Apache to mount cacophony. Example mod_wsgi files are located in contrib/mod_wsgi.

* cacophony.conf: The mod_wsgi configuration file. This should be modified and placed in /etc/httpd/conf.d/.
* cacophony.wsgi: The WSGI file that mod_wsgi will use. This should be modified and placed in the location noted in cacophony.conf

*Note*: When using mod_wsgi you will still need to set up authentication such as mod_auth_kerb.

## Usage

### curl
The authentication mechanism used in the front end webserver could be set up to use vastly different schemes. Instead of covering every possible authentication style which could be used we will work with two common ones in usage examples: htacces and kerberos.

The first command will look up to see if a known certificate already exists for an ENVIRONMENT/HOSTNAME. If it does it will return some basic json metadata. If it does not exist a 404 will be returned.

The second command will attempt to create a new certificate. If the certificate doesn't exist it will be created and returned, with the key, in pem format to the client. If a certificate has already been created for the host then a 409 with an error message will be returned.

*Note*: Setting up the front end proxy server for authentication is out of scope for this documentation.

### htaccess
```
$ curl -X GET --user "USERNAME" https://cacophony.example.com/api/v1/certificate/ENVIRONMENT/HOSTNAME/
Password:
... # 200 and json data if exists, otherwise 404 and error json
$ curl -X PUT -H "Content-Type: application/json" -d '{"email": "USER@EXAMPLE.COM"}' https://cacophony.example.com/api/v1/certificate/ENVIRONMENT/NEWHOST/
Password:
... # 201 and a pem (key + cert) returned
```

### kerberos
```
$ kinit -f USERNAME
Password for USERNAME@DOMAIN:
$ curl --delegation policy -X GET https://cacophony.example.com/api/v1/certificate/ENVIRONMENT/HOSTNAME/
... # 200 and json data if exists, otherwise 404 and error json
$ curl --delegation policy -X PUT -H "Content-Type: application/json" -d '{"email": "USER@EXAMPLE.COM"}' https://cacophony.example.com/api/v1/certificate/ENVIRONMENT/NEWHOST/
... # 201 and a pem (key + cert) returned
```
