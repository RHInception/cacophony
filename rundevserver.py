#!/usr/bin/env python

if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(0, os.path.realpath('src/'))
    os.environ['CACOPHONY_CONFIG'] = 'example-settings.json'
    print "DO NOT USE rundevserver IN PRODUCTION ENVIRONMENTS!"
    from cacophony import app
    app.run(debug=True)
