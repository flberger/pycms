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
import shutil
import os.path
import glob
import sys
import json
import re

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

                    raise RuntimeError("Source and result lines do not match when they should: '{}' vs. '{}'".format(separator[0], result_split[0]))

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
        
@pycms.command_line_function
def template(htmlroot, template):
    """Create a backup of `template` in `htmlroot`, as a preparation for a template update.
    """

    shutil.copy(os.path.join(htmlroot, "_templates", template),
                os.path.join(htmlroot, "_templates", template + ".old"))

    return

@pycms.command_line_function
def update(htmlroot):
    """Search for pending template changes in `htmlroot`, apply them to all pages using the template and delete template backups.
    """

    # Search for pending template changes
    #
    # NOTE: Not using os.path as glob uses Unix shell syntax
    #
    template_backups = glob.glob("{}/_templates/*.old".format(htmlroot))

    sys.stderr.write("template_backups == {}\n".format(template_backups))

    # Apply them to all pages using the template.
    # In passing, remove the path component.
    #
    changed_templates = [os.path.basename(path).rsplit(".old", 1)[0] for path in template_backups]

    sys.stderr.write("changed_templates == {}\n".format(changed_templates))

    uri_map_dict = {}

    with open(os.path.join(htmlroot, '_uri_template_map.json'), "rt", encoding = "utf8") as uri_map_file:

        uri_map_dict = json.loads(uri_map_file.read())

    # We need a map from template to URIs
    #
    template_map_dict = {}

    for uri in uri_map_dict.keys():

        if uri_map_dict[uri] in template_map_dict.keys():

            template_map_dict[uri_map_dict[uri]].append(uri)

        else:

            template_map_dict[uri_map_dict[uri]] = [uri]

    sys.stderr.write("template_map_dict == {}\n".format(template_map_dict))

    # There are two ways to do this: replay the template changes in
    # all files that use the template, or replaying what each file
    # changed in the original template to the new template. We'll go
    # for the latter, as these changes should be less ambiguous.
    #
    for template in changed_templates:

        for uri in template_map_dict[template]:

            sys.stderr.write("About to update '{}'\n".format(uri))

            page_replacements = None

            with open(os.path.join(htmlroot, "_templates", template + ".old"), "rt", encoding = "utf8") as original_template:

                with open(os.path.join(*[htmlroot] + uri.split("/") + ["index.html"]), "rt", encoding = "utf8") as page:
        
                    # Diff from old template to page. This yields the
                    # changes done to the template.
                    #
                    page_replacements = LineReplacement(original_template.read(),
                                                        page.read())

            with open(os.path.join(htmlroot, "_templates", template), "rt", encoding = "utf8") as new_template:

                with open(os.path.join(*[htmlroot] + uri.split("/") + ["index.html"]), "wt", encoding = "utf8") as page:
        
                    # Patch new template with diff. This replays the page's
                    # edits using the new template, yielding an updated page.
                    #
                    page.write(page_replacements.replace(new_template.read()))

        # Delete template backup
        #
        os.remove(os.path.join(htmlroot, "_templates", template + ".old"))

    return
