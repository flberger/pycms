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

import optparse
import pycms
import pycms.serve

def main():
    """Parse options and configuration and call serve().
    """

    # Originally taken from bbk3.run

    parser = optparse.OptionParser(version = pycms.VERSION,
                                   usage = "Usage: %prog [options] command [htmlroot]")

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

    # Conditionally turn off Autoreloader
    #
    if not options.autoreload:

        pycms.serve.cherrypy.engine.autoreload.unsubscribe()

    pycms.serve.CONFIG_DICT["global"]= {"server.socket_host" : "0.0.0.0",
                                        "server.socket_port" : options.port,
                                        "server.thread_pool" : options.threads}

    if not len(args):

        parser.print_help()

        raise SystemExit

    if not args[0] in pycms.COMMAND_LINE_COMMANDS:

        # My first generator comprehension, saving list memory. :-)
        #
        commands = ", ".join(("'{}'".format(item) for item in pycms.COMMAND_LINE_COMMANDS))
        
        raise RuntimeError("Unknown command '{}'. Please use one of {}.".format(args[0],
                                                                                commands))

    # Filter commands that require a parameter
    #
    if args[0] in ("envinit", "serve"):

        if len(args) < 2:

            raise RuntimeError("Please specify the root directory containing the working environment for command '{}'.".format(args[0]))

        # Now for some Python magic.
        # Call the function given as command on the command line.
        #
        pycms.COMMAND_LINE_COMMANDS[args[0]](args[1])

    else:

        # Call without parameters.
        #
        pycms.COMMAND_LINE_COMMANDS[args[0]]()

    return

if __name__ == "__main__":

    main()
