#!/usr/bin/env python
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

if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(0, os.path.realpath('src/'))
    os.environ['CACOPHONY_CONFIG'] = 'example-settings.json'
    print "DO NOT USE rundevserver IN PRODUCTION ENVIRONMENTS!"
    from cacophony import app
    app.run(debug=True)
