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

from sys import stderr
import os
import os.path
import json

VERSION = "0.1.0"
COMMAND_LINE_COMMANDS = {}

# My first useful decorator, if I remember correctly.
#
def command_line_function(func):
    """Register the name of the function given as a command line command.
    """

    stderr.write("Registering '{}' as a command line command\n".format(func.__name__))

    COMMAND_LINE_COMMANDS[func.__name__] = func

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
