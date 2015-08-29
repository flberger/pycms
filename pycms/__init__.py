"""A lightweight web content management system.

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

import sys
import os.path
import json
import shutil
import glob
import sys
import re

VERSION = "0.1.0"

TEMPLATES_FOLDER = "_templates"

STATIC_FOLDER = "static"

SPECIAL_FOLDERS = (TEMPLATES_FOLDER, STATIC_FOLDER)

CONFIG_DICT = {}

class Instance:
    """Represents a hierarchy of pages, along with templates.

       Attributes:

       Instance.htmlroot
           The path to this Instance's root directory.
    """

    def __init__(self, htmlroot):
        """Initialise. `htmlroot` is the path to this Instance's root directory.
        """

        self.htmlroot = htmlroot

        if htmlroot[-1] == "/":

            # Normalise
            #
            self.htmlroot = htmlroot[:-1]

        return

    def envinit(self):
        """Create a working directory consisting of the minimum directory and files necessary to run a pycms instance.
        """

        os.mkdir(self.htmlroot)

        with open(os.path.join(self.htmlroot, "index.html"), "wt", encoding = "utf8") as htmlfile:

            # TODO: This should actually be generated from the first template.
            #
            htmlfile.write('''<!DOCTYPE html>
    <html>
    <meta charset="utf-8"/>
    <head>
        <title>
    pycms Instance Index
        </title>
    </head>
    <body>
        <h1>pycms Instance Index</h1>
        <p>Welcome to your pycms instance.</p>
    </body>
    </html>
    ''')

        os.mkdir(os.path.join(self.htmlroot, TEMPLATES_FOLDER))

        with open(os.path.join(self.htmlroot, TEMPLATES_FOLDER, "index_template.html"), "wt", encoding = "utf8") as templatefile:

            templatefile.write('''<!DOCTYPE html>
    <html>
    <meta charset="utf-8"/>
    <head>
        <title>
            TITLE
        </title>
    </head>
    <body>
    CONTENT
    </body>
    </html>
    ''')

        with open(os.path.join(self.htmlroot, "_uri_template_map.json"), "wt", encoding = "utf8") as mapfile:

            mapfile.write(json.dumps({"/": "index_template.html"},
                                     ensure_ascii = False))

        os.mkdir(os.path.join(self.htmlroot, STATIC_FOLDER))
        
        with open(os.path.join(self.htmlroot, STATIC_FOLDER, "index.html"), "wt", encoding = "utf8") as htmlfile:

            htmlfile.write('''<!DOCTYPE html>
    <html>
    <meta charset="utf-8"/>
    <head>
        <title>
    Forbidden
        </title>
    </head>
    <body>
        <p>You do not have access to this directory.</p>
    </body>
    </html>
    ''')

        return
        
    def create_page(self, uri, template):
        """Create and register a new page under the given URI using the given template.
        """

        if not uri.startswith("/"):

            raise RuntimeError("The URI parameter must start with a slash.")

        components = uri.strip("/").split("/")

        if components[0] in SPECIAL_FOLDERS:

            raise RuntimeError('"/{}/" is a special URI and can not be re-created.'.format(components[0]))

        path = [self.htmlroot]

        path += components

        path_with_index = path + ["index.html"]
        
        if uri == "/":

            if os.path.exists(os.path.join(*path_with_index)):

                raise RuntimeError('URI "{}" can not be created because "{}" already exists.'.format(uri, os.path.join(*path_with_index)))

        else:

            if os.path.exists(os.path.join(*path)):

                raise RuntimeError('URI "{}" can not be created because "{}" already exists.'.format(uri, os.path.join(*path)))

            os.makedirs(os.path.join(*path))

        shutil.copy(os.path.join(self.htmlroot, TEMPLATES_FOLDER, template), os.path.join(*path_with_index))

        uri_map_dict = {}

        with open(os.path.join(self.htmlroot, "_uri_template_map.json"), "rt", encoding = "utf8") as uri_map_file:

            uri_map_dict = json.loads(uri_map_file.read())

        uri_map_dict["/{}".format(uri.strip("/"))] = template

        with open(os.path.join(self.htmlroot, "_uri_template_map.json"), "wt", encoding = "utf8") as uri_map_file:

            uri_map_file.write(json.dumps(uri_map_dict,
                                          sort_keys = True,
                                          ensure_ascii = False))

        return
        
    def edit_template(self, template):
        """Create a backup of `template` in `htmlroot`, as a preparation for a template update.
        """

        shutil.copy(os.path.join(self.htmlroot, TEMPLATES_FOLDER, template),
                    os.path.join(self.htmlroot, TEMPLATES_FOLDER, template + ".old"))

        return

    def update(self):
        """Search for pending template changes, apply them to all pages using the template and delete template backups.
        """

        # Search for pending template changes
        #
        # NOTE: Not using os.path as glob uses Unix shell syntax
        #
        template_backups = glob.glob("/".join((self.htmlroot, TEMPLATES_FOLDER, "*.old")))

        sys.stderr.write("template_backups == {}\n".format(template_backups))

        # Apply them to all pages using the template.
        # In passing, remove the path component.
        #
        changed_templates = [os.path.basename(path).rsplit(".old", 1)[0] for path in template_backups]

        sys.stderr.write("changed_templates == {}\n".format(changed_templates))

        uri_map_dict = {}

        with open(os.path.join(self.htmlroot, "_uri_template_map.json"), "rt", encoding = "utf8") as uri_map_file:

            uri_map_dict = json.loads(uri_map_file.read())

        # We need a map from template to URIs
        #
        template_map_dict = {}

        for uri in uri_map_dict.keys():

            if uri_map_dict[uri] in template_map_dict.keys():

                template_map_dict[uri_map_dict[uri]].append(uri)

            else:

                template_map_dict[uri_map_dict[uri]] = [uri]

        # For predictability, sort the URI lists
        #
        for template in template_map_dict.keys():

            template_map_dict[template].sort()

        sys.stderr.write("template_map_dict == {}\n".format(template_map_dict))

        # There are two ways to do this: replay the template changes in
        # all files that use the template, or replaying what each file
        # changed in the original template to the new template. We'll go
        # for the latter, as these changes should be less ambiguous.
        #
        for template in changed_templates:

            for uri in template_map_dict[template]:

                sys.stderr.write("About to update '{}' using template '{}'\n".format(uri, template))

                page_replacements = None

                with open(os.path.join(self.htmlroot, TEMPLATES_FOLDER, template + ".old"), "rt", encoding = "utf8") as original_template:

                    with open(os.path.join(*[self.htmlroot] + uri.split("/") + ["index.html"]), "rt", encoding = "utf8") as page:

                        # Diff from old template to page. This yields the
                        # changes done to the template.
                        #
                        page_replacements = LineReplacement(original_template.read(),
                                                            page.read())

                with open(os.path.join(self.htmlroot, TEMPLATES_FOLDER, template), "rt", encoding = "utf8") as new_template:

                    with open(os.path.join(*[self.htmlroot] + uri.split("/") + ["index.html"]), "wt", encoding = "utf8") as page:

                        # Patch new template with diff. This replays the page's
                        # edits using the new template, yielding an updated page.
                        #
                        page.write(page_replacements.replace(new_template.read()))

            # Delete template backup
            #
            os.remove(os.path.join(self.htmlroot, TEMPLATES_FOLDER, template + ".old"))

        return

    def remove_page(self, uri):
        """Remove the page page under the given URI.
        """

        # TODO: Remove all pages starting with uri

        if not uri.startswith("/"):

            raise RuntimeError("The URI parameter must start with a slash.")

        if uri == "/":

            # We do not want to remove the htmlroot directory.
            # Remove the root index page only.

            os.remove(os.path.join(self.htmlroot, "index.html"))

        else:

            components = uri.strip("/").split("/")

            if components[0] in SPECIAL_FOLDERS:

                raise RuntimeError('"/{}/" is a special URI and can not be removed.'.format(components[0]))

            path = [self.htmlroot]

            path += components

            if not os.path.exists(os.path.join(*path)):

                raise RuntimeError('URI "{}" can not be removed because "{}" does not exist.'.format(uri, os.path.join(*path)))

            shutil.rmtree(os.path.join(*path))

        uri_map_dict = {}

        with open(os.path.join(self.htmlroot, "_uri_template_map.json"), "rt", encoding = "utf8") as uri_map_file:

            uri_map_dict = json.loads(uri_map_file.read())

        del uri_map_dict["/{}".format(uri.strip("/"))]

        with open(os.path.join(self.htmlroot, "_uri_template_map.json"), "wt", encoding = "utf8") as uri_map_file:

            uri_map_file.write(json.dumps(uri_map_dict,
                                          sort_keys = True,
                                          ensure_ascii = False))

        return
        
    def serve(self, test = False):
        """Serve the CMS instance from the root .

           If test is set to True, the instance will terminate after a
           short while. This is a feature for automated testing.
        """

        # TODO: Move cherrypy code
        #
        # root = CMS(self.htmlroot)
        #
        # config_dict_final = {"/" : {"tools.sessions.on" : True,
        #                            "tools.sessions.timeout" : 60}}
        #
        # config_dict_final.update(CONFIG_DICT)

        import http.server
        import socketserver

        # SimpleHTTPRequestHandler serves from the current directory,
        # so change accordingly

        original_cwd = os.getcwd()

        try:
            os.chdir(self.htmlroot)

        except FileNotFoundError:
            
            raise RuntimeError("Working environment directory 'pycmsroot' not found. Did you run pycms.envinit(\"pycmsroot\")?")

        handler = http.server.SimpleHTTPRequestHandler

        httpd = socketserver.TCPServer(("", 8000), handler)

        exit_thread = None

        if test:

            sys.stderr.write("Testing enabled, terminating after timeout\n")

            def exit_after_timeout():

                import time

                start_time = time.perf_counter()

                # Wait 2 seconds
                #
                while time.perf_counter() - start_time < 2.0:

                    time.sleep(0.1)

                sys.stderr.write("About to terminate web server\n")

                # NOTE: Terminate web server here
                # cherrypy.engine.exit()

                httpd.shutdown()
                
                return

            import threading

            exit_thread = threading.Thread(target = exit_after_timeout,
                                           name = "exit_thread")

            sys.stderr.write("Starting exit thread\n")

            exit_thread.start()

        # NOTE: Start up web server here
        # cherrypy.quickstart(root, config = config_dict_final)

        sys.stderr.write("Serving HTTP on port 8000\n")
        
        httpd.serve_forever()

        os.chdir(original_cwd)

        if test:

            sys.stderr.write("Waiting for exit thread\n")

            exit_thread.join()

            sys.stderr.write("Exit thread joined\n")

        return

class LineReplacement:
    """Compute diffs and patches for multi-line strings where single lines have been replaced.

       The lines being replaced must me unique in the source file.
    """

    def __init__(self, source, result):
        """Initialise, and compute the replacements done to `source` in `result`.
        
           `source` and `result` are expected to be multi-line strings.
        """

        source_split = source.splitlines(keepends = True)

        result_split = result.splitlines(keepends = True)

        self.replacements = {}

        # Okay I've been thinking about this for a while. Diffs and
        # patches are by no means trivial. An especially in the case
        # at hand it is easy to construct replacements that are
        # ambiguous and very hard to parse.
        #
        # So, trying to be clever will only take us so far. Instead,
        # what we do is go with a very naive way, using previous
        # knowledge about the replacement pattern.

        # Split the source at lines with single uppercase words
        # + underscore, yielding a list of separator - token -
        # separator ... successions
        #
        tokenised = [[]]

        for line in source_split:

            if re.match("^[A-Z_]+$", line.strip()):

                tokenised.append(line.strip())

                tokenised.append([])

            else:

                # NOTE: Expecting this to happen for the first line
                #
                tokenised[-1].append(line)

        if tokenised[-1] == []:

            del tokenised[-1]

        while tokenised:

            # Remove first separator in source and result, which should
            # be common.
            #
            separator = tokenised[0]

            while separator:

                if separator[0] == result_split[0]:

                    del separator[0]

                    del result_split[0]

                else:

                    # TODO: This can only be recovered from when changing the *.old backup files. These should be deleted, i.e. editing the affected templates should probably be aborted.
                    #
                    raise RuntimeError("Source and result lines do not match when they should: '{}' vs. '{}'\n(Hint: The source line is not a valid placeholder, if that was intended.)".format(separator[0], result_split[0]))

            # Remove the emptied list
            #
            del tokenised[0]

            # Something left?
            #
            if tokenised:

                # Collect all lines after the line replacing the first token
                # until the first match of the next separator is found.
                # Note that this will easily yield false positives, as the
                # separator pattern might be part of the replacement.
                #
                replacement = []

                # NOTE: We expect this to terminate at some point, else it is no valid replacement anyway.
                #
                while tokenised[1][0] != result_split[0]:

                    replacement.append(result_split.pop(0))

                # Lines match now. Store replacement with enclosing
                # whitespace removed, and repeat from removing the
                # first separator.
                #
                self.replacements[tokenised[0]] = "".join(replacement).strip()

                del tokenised[0]

        sys.stderr.write("Initialised with replacements = {}\n".format(self.replacements))
        
        return

    def replace(self, input):
        """Replace occurences of LineReplacement.replacements keys in input with their respecitve values, and return the result.
        """

        for key in self.replacements.keys():

            sys.stderr.write("Replacing '{}'\n".format(key))
            
            input = input.replace(key, self.replacements[key])

        return input
        
class CMS:
    """CMS base class and root of a CherryPy site.

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
