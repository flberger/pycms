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

class PycmsWebAdminHandler(http.server.BaseHTTPRequestHandler):
    """Request handler to display and manage the pycms web admin interface.
    """

    def do_GET(self):
        """Handle a GET request.
        """

        self.test_output()

        return

    def do_POST(self):
        """Handle a POST request.
        """
        
        self.test_output()
        
        return

    def test_output(self):
        
        parsed_uri = urllib.parse.urlparse(self.path)
        parsed_query = urllib.parse.parse_qs(parsed_uri.query)

        page = quickhtml.Page("pycms Web Admin Test")

        page.append("<h1>pycms Web Admin Test</h1>")

        page.append("""<pre>
urlparse == {0}
query == {1}</pre>
<h2>Headers</h2>
<pre>
{2}
</pre>""".format(parsed_uri, parsed_query, self.headers))

        if "content-length" in self.headers:
            
            #page.append("<h2>Input</h2><pre>{}</pre>".format(self.rfile.read(int(self.headers["content-length"]))))
            page.append("<h2>Input</h2><pre>{}</pre>".format(cgi.FieldStorage(fp = self.rfile, headers = self.headers, environ = {"REQUEST_METHOD": "POST"}).keys()))

        form = quickhtml.Form("/process", "POST", "<br>", "Send")

        form.add_fieldset("Test Form")
        
        form.add_input("Test", "text", "testinput", value = "blubb")

        page.append(str(form))

        self.wfile.write("HTTP/1.1 200 OK\nContent-type: text/html\n\n".encode("utf8"))

        self.wfile.write(str(page).encode("utf8"))

        return
        
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

    instance = pycms.Instance(args[0])

    server = socketserver.TCPServer(("", options.port), PycmsWebAdminHandler)

    stderr.write("Serving at port {}\n".format(options.port))
    
    server.serve_forever()

    return

if __name__ == "__main__":

    main()
