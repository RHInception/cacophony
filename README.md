# cacophony
Simple REST Api for automagic SSL certificate generation.


## Unittests
Use *nosetests -v --with-cover --cover-package cacophony test/* from the main directory to execute unittests. This will use the test/Test-CA/ CA.

## Configuration
Configuration of the server is done in JSON and is by default kept in the current directories settings.json file.

You can override the location by setting `CACOPHONY_CONFIG` environment variable.

| Name            | Type | Parent | Value                                                               |
|-----------------|------|--------|---------------------------------------------------------------------|
| AUTH\_DECORATOR | str  | None   | cacophony.decorators:remote\_user\_required (module.name:decorator) |
| CA              | dict | None   | A dictionary holding CA configuration data                          |
| "NAME"          | dict | CA     | Configuration info for the CA called "NAME"                         |
| privKey         | str  | "NAME" | Path to the CA's private key.                                       |
| privPass        | str  | "NAME" | Password for CA.                                                    |
| pubCert         | str  | "NAME" | Path to the public cert.                                            |
| serial          | str  | "NAME" | Path to the CA's serial file.                                       |
| index           | str  | "NAME" | Path to the CA's index file.                                        |
| keySize         | int  | "NAME" | Key size to use                                                     |
| validTime       | int  | "NAME" | Length of time the certificates will be valid for.                  |


### Example Config
```json
{
    "DEBUG": true,
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
            "validTime":  31536000
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
| Method | Inputs                    | Input Type | Respones Type              | Auth Required |
| :----: | :-----------------------: | :--------: | :------------------------: | :-----------: |
| GET    | None                      | None       | json                       | Yes           |
| PUT    | email,[insecure\_policy]  | json       | json on error, txt on cert | Yes           |
