"""A web content management system based on CherryPy.

   Copyright (c) 2013 Florian Berger <fberger@florian-berger.de>
"""

# This file is part of pycms.
#
# pycms is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pycms is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pycms.  If not, see <http://www.gnu.org/licenses/>.

# Work started on 30. Sep 2013.

import optparse
import cherrypy

VERSION = "0.1.0"

class CMS:
    """CMS base class and root of the CherryPy site.
    """

    def __init__(self):
        """Initialise.
        """

        self.exposed = True

        return

    def __call__(self):
        """Called by CherryPy to render this object.
        """

        return "Hello World!"

def main():
    """Set up and run a pycms instance.
    """

    # Taken from bbk3.run

    parser = optparse.OptionParser(version = VERSION)

    parser.add_option("-p", "--port",
                      action = "store",
                      type = "int",
                      default = 8000,
                      help = "The port to listen on. Default: 8000")

    parser.add_option("-t", "--threads",
                      action = "store",
                      type = "int",
                      default = 10,
                      help = "The number of worker threads to start. Default: 10")

    parser.add_option("-a", "--autoreload",
                      action = "store_true",
                      dest = "autoreload",
                      default = False,
                      help = "Turn on CherryPy's auto reloading feature. Default: Off.")

    options, args = parser.parse_args()

    root = CMS()

    config_dict = {"/" : {"tools.sessions.on" : True,
                          "tools.sessions.timeout" : 60},
                   "global" : {"server.socket_host" : "0.0.0.0",
                               "server.socket_port" : options.port,
                               "server.thread_pool" : options.threads}}

    # Conditionally turn off Autoreloader
    #
    if not options.autoreload:

        cherrypy.engine.autoreload.unsubscribe()

    cherrypy.quickstart(root, config = config_dict)

    return

if __name__ == "__main__":

    main()
