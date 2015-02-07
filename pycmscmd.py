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
import cmd
import glob
import os.path

class PycmsCmd(cmd.Cmd):
    """Cmd subclass with pycms-specific methods.
    """

    def __init__(self, instance):
        """Initialise.
        """

        self.instance = instance
        
        cmd.Cmd.__init__(self)

        self.prompt = "pycms: "

        self.intro = """Welcome to the pycms command line interface.
Type '?' for help and 'EOF' to exit.
htmlroot = {}""".format(self.instance.htmlroot)

        return

    def emptyline(self):
        """Ignore empty input, overriding default behaviour.
        """

        return

    # Begin pycms.Instance method dispatchers
    #
    # TODO: Ideally, these would be added automatically via some decorator or parser by calling `setattr()` on the class.
    # But this is simple and straightforward.

    def do_envinit(self, arg):
        """do_envinit documentation
        """

        self.instance.envinit()

        return False

    def do_create_page(self, arg):
        """do_create_page documentation
        """

        self.instance.create_page(*arg.split())

        return False

    def do_edit_template(self, arg):
        """do_edit_template documentation
        """

        self.instance.edit_template(arg)

        return False

    def do_update(self, arg):
        """do_update documentation
        """

        self.instance.update()

        return False

    def do_serve(self, arg):
        """do_serve documentation
        """

        self.instance.serve()

        return False

    # End pycms.Instance method dispatchers

    def completedefault(self, text, line, begidx, endidx):
        """Complete using the template file names.
        """

        # TODO: A template file list really should be available in the instance.
        #
        template_paths = glob.glob("{}/_templates/*.html".format(self.instance.htmlroot))

        template_files = [os.path.basename(path) for path in template_paths]

        return template_files
        
    def do_EOF(self, arg):
        """Exit the command line interpreter.
        """

        return True

def main():
    """Run a command line interpreter.
    """

    # # Originally taken from bbk3.run

    parser = optparse.OptionParser(version = pycms.VERSION,
                                   usage = "Usage: %prog [options] htmlroot")

    # parser.add_option("-p", "--port",
    #                   action = "store",
    #                   type = "int",
    #                   default = 8000,
    #                   help = "The port to listen on. Default: 8000")

    # parser.add_option("-t", "--threads",
    #                   action = "store",
    #                   type = "int",
    #                   default = 10,
    #                   help = "The number of worker threads to start. Default: 10")

    # parser.add_option("-a", "--autoreload",
    #                   action = "store_true",
    #                   dest = "autoreload",
    #                   default = False,
    #                   help = "Turn on CherryPy's auto reloading feature. Default: Off.")

    options, args = parser.parse_args()

    # # Conditionally turn off Autoreloader
    # #
    # if not options.autoreload:

    #     pycms.cherrypy.engine.autoreload.unsubscribe()

    # pycms.CONFIG_DICT["global"]= {"server.socket_host" : "0.0.0.0",
    #                               "server.socket_port" : options.port,
    #                               "server.thread_pool" : options.threads}

    if not len(args):

        parser.print_help()

        raise SystemExit

    instance = pycms.Instance(args[0])
    
    pycms_cmd = PycmsCmd(instance)

    pycms_cmd.cmdloop()

    return

if __name__ == "__main__":

    main()
