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

# Work started on 30. Sep 2013. This is a rewrite of BBk3 based on a different concept.

# TODO: parse a single command line command for module-level functions.

import optparse
import cherrypy
from sys import stderr
import os
import os.path
import json

VERSION = "0.1.0"
COMMAND_LINE_COMMANDS = []
CONFIG_DICT = {}

class CMS:
    """CMS base class and root of the CherryPy site.

       Attributes:

       CMS.htmlroot
           A string, holding the root directory to serve from and save to.
    """

    def __init__(self, htmlroot):
        """Initialise.
        """

        if not os.path.isdir(htmlroot):

            raise RuntimeError("Working environment directory '{0}' not found. Did you run pycms.envinit(\"{0}\")?".format(htmlroot))

        self.htmlroot = htmlroot

        self.exposed = True

        return

    def __call__(self):
        """Called by CherryPy to render this object.
        """

        return "Hello World!"

# My first useful decorator, if I remember correctly.
#
def command_line_function(func):
    """Register the name of the function given as a command line command.
    """

    stderr.write("Registering '{}' as a command line command\n".format(func.__name__))

    COMMAND_LINE_COMMANDS.append(func.__name__)

    return func

@command_line_function
def envinit(htmlroot):
    """Create a working directory consisting of the minimum directory and files necessary to run a pycms instance.

       htmlroot is the path to the directory to be created.
    """

    os.mkdir(htmlroot)

    with open(os.path.join(htmlroot, "index.html"), "wt", encoding = "utf8") as htmlfile:

        # TODO: This should actually be generated from the first template.
        #
        htmlfile.write('''<!DOCTYPE html>
<html>
<meta charset="utf-8"/>
<head>
    <title>pycms Instance Index</title>
</head>
<body>
    <h1>pycms Instance Index</h1>
    <p>Welcome to your pycms instance.</p>
</body>
</html>''')

    os.mkdir(os.path.join(htmlroot, "_templates"))

    with open(os.path.join(htmlroot, "_templates", "index_template.html"), "wt", encoding = "utf8") as templatefile:

        templatefile.write('''<!DOCTYPE html>
<html>
<meta charset="utf-8"/>
<head>
    <title>TITLE</title>
</head>
<body>
CONTENT
</body>
</html>''')

    with open(os.path.join(htmlroot, "_uri_template_map.json"), "wt", encoding = "utf8") as mapfile:

        mapfile.write(json.dumps({"/index.html": "/_templates/index_template.html"},
                                 ensure_ascii = False))

    return

def envparse(htmlroot, cms_instance):
    """Parse the working environment in directory 'htmlroot', and populate the CMS instance 'cms_instance' with the results.
    """

    # TODO: This is a demo, catching only the index page. Replace with tree parser.
    # TODO: parse URI template mapping

    page_content = None

    with open(os.path.join(htmlroot, "index.html"), "rt", encoding = "utf8") as page_file:

        page_content = page_file.read()

    # Hand the string over at function definition time, which stores a
    # reference to the current value. Using the variable at execution
    # time would point to the value present then.
    #
    def return_page(self, return_value = page_content):

        return return_value

    # Expose for CherryPy
    #
    return_page.exposed = True

    # "Instances of arbitrary classes can be made callable by defining
    # a __call__() method in their class."
    # python-docs-3.3.0/html/reference/datamodel.html#types
    #
    cms_instance.__class__.__call__ = return_page

    return

@command_line_function
def serve(htmlroot, test = False):
    """Serve the CMS from the directory `htmlroot`.

       If test is set to True, the instance will terminate after a
       short while. This is a feature for automated testing.
    """

    root = CMS(htmlroot)

    config_dict_final = {"/" : {"tools.sessions.on" : True,
                                "tools.sessions.timeout" : 60}}

    config_dict_final.update(CONFIG_DICT)

    exit_thread = None

    if test:

        stderr.write("Testing enabled, terminating after timeout\n")

        def exit_after_timeout():

            import time

            start_time = time.perf_counter()

            # Wait 2 seconds
            #
            while time.perf_counter() - start_time < 2.0:

                time.sleep(0.1)

            stderr.write("About to terminate CherryPy engine\n")

            cherrypy.engine.exit()

            return

        import threading

        exit_thread = threading.Thread(target = exit_after_timeout,
                                       name = "exit_thread")

        stderr.write("Starting exit thread\n")

        exit_thread.start()

    cherrypy.quickstart(root, config = config_dict_final)

    if test:

        stderr.write("Waiting for exit thread\n")

        exit_thread.join()

        stderr.write("Exit thread joined\n")

    return

def main():
    """Parse options and configuration and call serve().
    """

    # Originally taken from bbk3.run

    parser = optparse.OptionParser(version = VERSION,
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

        cherrypy.engine.autoreload.unsubscribe()

    CONFIG_DICT["global"]= {"server.socket_host" : "0.0.0.0",
                            "server.socket_port" : options.port,
                            "server.thread_pool" : options.threads}

    if not len(args):

        parser.print_help()

        raise SystemExit

    if not args[0] in COMMAND_LINE_COMMANDS:

        # My first generator comprehension, saving list memory. :-)
        #
        commands = ", ".join(("'{}'".format(item) for item in COMMAND_LINE_COMMANDS))
        
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
        globals()[args[0]](args[1])

    else:

        # Call without parameters.
        #
        globals()[args[0]]()

    return

if __name__ == "__main__":

    main()
