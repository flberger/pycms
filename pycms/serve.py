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

import pycms
from pycms import command_line_function
from sys import stderr
import cherrypy
import os.path

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
