"""A lightweight web content management system.

   Copyright (c) 2015 Florian Berger <mail@florian-berger.de>
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

# Work started on 30. August 2015

import optparse
from sys import stderr
import pycms
import http.server
import socketserver
import urllib
import quickhtml
import cgi
import os.path
# For listing URIs
import json
# For listing templates
import glob

URI_HANDLERS = {}

# Using a list to be able to change it at runtime
#
INSTANCE = [None]

def exposed(func):
    """Register func by its name in PycmsWebAdminHandler.uri_handlers, mapping the '/funcname' to handle it.

       Registered functions are supposed to be instance methods, to
       be called with keyword arguments, supplying sensible defaults,
       accepting any excess keyword arguments, and returning a string.

       Example:

       @exposed
       def test(self, testinput = None, **kwargs):

           result = "testinput == {0}\n".format(testinput)

           result += "Excess arguments == {}\n".format(kwargs)

           return result

       This method is callable via the '/test?testinput=spam&excess=eggs' URI.
    """

    uri = "/{}".format(func.__name__)

    URI_HANDLERS[uri] = func

    stderr.write("Registering URI '{}'\n".format(uri))

    return func

class PycmsWebAdminHandler(http.server.BaseHTTPRequestHandler):
    """Request handler to display and manage the pycms web admin interface.

       Attributes:

       PycmsWebAdminHandler.uri_handlers
           Dict mapping URI strings to handler methods, filled by the
           exposed() decorator.
    """

    def do_GET(self):
        """BaseHTTPRequestHandler standard method: handle a GET request.
        """

        self.parse_and_handle()

        return

    def do_POST(self):
        """BaseHTTPRequestHandler standard method: handle a POST request.
        """
        
        self.parse_and_handle()
        
        return

    def parse_and_handle(self):
        
        parsed_uri = urllib.parse.urlparse(self.path)
        parsed_query = urllib.parse.parse_qs(parsed_uri.query)

        stderr.write("urlparse == {}\n".format(parsed_uri))

        stderr.write("query == {}\n".format(parsed_query))

        # Simulate CGI
        #
        environment = {"REQUEST_METHOD": self.command,
                       "QUERY_STRING": parsed_uri.query}

        if "content-length" in self.headers:

            environment["CONTENT_LENGTH"] = self.headers["content-length"]

        if "content-type" in self.headers:

            environment["CONTENT_TYPE"] = self.headers["content-type"]

        else:

            # Force cgi module to parse query string
            #
            environment["CONTENT_TYPE"] = "application/x-www-form-urlencoded"

            self.headers["Content-type"] = "application/x-www-form-urlencoded"

        fieldstorage = cgi.FieldStorage(fp = self.rfile, headers = self.headers, environ = environment)

        arguments = {}

        for key in fieldstorage.keys():

            arguments[key] = fieldstorage.getfirst(key)

        stderr.write("arguments == {}".format(arguments))
            
        content = ""
        
        try:
            content = URI_HANDLERS[parsed_uri.path](self, **arguments)

            self.wfile.write("HTTP/1.1 200 OK\nContent-type: text/html\n\n".encode("utf8"))

            self.wfile.write(content.encode("utf8"))

        except KeyError:

            self.wfile.write("HTTP/1.1 404 NOT FOUND\nContent-type: text/plain\n\n".encode("utf8"))

            self.wfile.write("Error 404: '{}' not found".format(parsed_uri.path).encode("utf8"))

        return

    @exposed
    def admin(self, **kwargs):
        """Render the admin landing page
        """

        page = quickhtml.Page("pycms Web Admin")

        page.append("<h1>pycms Web Admin</h1>")

        page.append("<h2>Create New Page</h2>")

        form = quickhtml.Form(action = "/edit_template", method = "POST", separator = "<br>", submit_label = "Create Page")

        form.add_fieldset("Create Page")

        form.add_input(label = "URI:", type = "text", name = "uri")

        # TODO: Taken from pycmscmd.completedefault()
        # TODO: A template file list really should be available in the instance.
        #
        template_paths = glob.glob("{}/_templates/*.html".format(INSTANCE[0].htmlroot))

        template_paths = [os.path.basename(path) for path in template_paths]

        form.add_drop_down_list(label = "Template:", name = "template", list = template_paths)

        page.append(str(form))

        page.append("<h2>URI List</h2>")
        
        # TODO: Taken from Instance.create_page. Instead, the instance should provide a method to get the list.

        uri_map_dict = {}

        with open(os.path.join(INSTANCE[0].htmlroot, '_uri_template_map.json'), "rt", encoding = "utf8") as uri_map_file:

            uri_map_dict = json.loads(uri_map_file.read())

        uris = list(uri_map_dict.keys())

        uris.sort()

        page.append("<ul>")

        for uri in uris:

            page.append("<li>{0} [{1}]</li>".format(uri, uri_map_dict[uri]))

        page.append("</ul>")

        return str(page)
        
    @exposed
    def edit_template(self, uri = None, template = None,  **kwargs):
        
        page = quickhtml.Page("pycms Web Admin")

        page.append("<h1>Create '{}'</h1>".format(uri))

        page.append('<p><a href="/admin">Back to web admin interface</a></p>')

        page.append("<p>Using template '{}'</p>".format(template))

        form = quickhtml.Form(action = "/save", method = "POST", separator = "<br>", submit_label = "Save Page")

        form.add_fieldset("Edit Page")

        with open(os.path.join(INSTANCE[0].htmlroot, pycms.TEMPLATES_FOLDER, template), "rt", encoding = "utf8") as f:

            form.add_textarea(name = "page_content", content = f.read())

        form.add_hidden("uri", uri)

        form.add_hidden("template", template)

        page.append(str(form))

        return str(page)

    @exposed
    def save(self, page_content = None, uri = None, template = None, **kwargs):
        
        page = quickhtml.Page("pycms Web Admin")

        page.append("<h1>Saving '{}'</h1>".format(uri))

        page.append("<p>Creating page ...")

        stderr.write("WARNING: TODO: Writing using unchecked parameters\n")
        
        INSTANCE[0].create_page(uri, template)

        page.append(" done.</p>")
        
        page.append("<p>Saving edited template as page ...")

        components = uri.strip("/").split("/")

        path = [INSTANCE[0].htmlroot]

        path += components

        path_with_index = path + ["index.html"]
        
        with open(os.path.join(*path_with_index), "wt", encoding = "utf8") as f:

            f.write(page_content)

        page.append(" done.</p>")
        
        page.append('<p><a href="/admin">Back to web admin interface</a></p>')

        return str(page)

def main():
    """Run a web-based admin interface.
    """

    parser = optparse.OptionParser(version = pycms.VERSION,
                                   usage = "Usage: %prog [options] htmlroot")

    parser.add_option("-p", "--port",
                      action = "store",
                      type = "int",
                      default = 8001,
                      help = "The port to listen on. Default: 8001")

    options, args = parser.parse_args()

    if not len(args):

        parser.print_help()

        raise SystemExit

    INSTANCE[0] = pycms.Instance(args[0])

    stderr.write("Created instance with htmlroot == '{}'\n".format(INSTANCE[0].htmlroot))

    server = socketserver.TCPServer(("", options.port), PycmsWebAdminHandler)

    stderr.write("Serving at port {}\n".format(options.port))
    
    server.serve_forever()

    return

if __name__ == "__main__":

    main()
