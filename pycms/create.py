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
import os.path
import os
import shutil
import json

@pycms.command_line_function
def page(htmlroot, uri, template):
    """Create and register a new page under the given URI using the given template.
    """

    if not uri.startswith("/"):

        raise RuntimeError("The URI parameter must start with a slash.")

    path = [htmlroot]

    path += [component for component in uri.strip("/").split("/")]

    if os.path.exists(os.path.join(*path)):

        raise RuntimeError('URI "{}" can not be created because it already exists.'.format(uri))

    os.makedirs(os.path.join(*path))

    path += ["index.html"]

    shutil.copy(os.path.join(htmlroot, "_templates", template), os.path.join(*path))

    uri_map_dict = {}
    
    with open(os.path.join(htmlroot, '_uri_template_map.json'), "rt", encoding = "utf8") as uri_map_file:

        uri_map_dict = json.loads(uri_map_file.read())

    uri_map_dict["/{}".format(uri.strip("/"))] = template
    
    with open(os.path.join(htmlroot, '_uri_template_map.json'), "wt", encoding = "utf8") as uri_map_file:

        uri_map_file.write(json.dumps(uri_map_dict,
                                      sort_keys = True,
                                      ensure_ascii = False))

    return
