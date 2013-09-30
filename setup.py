"""pycms Setup Script

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

# Work started on 30. Sep 2013.

import os.path
import pycms

PACKAGE = "pycms"

# Fallback
#
from distutils.core import setup

SCRIPTS = ["pycms.py"]

EXECUTABLES = []

try:
    import cx_Freeze

    setup = cx_Freeze.setup

    EXECUTABLES = [cx_Freeze.Executable(path) for path in SCRIPTS]

except ImportError:

    print("Warning: the cx_Freeze module could not be imported. You will not be able to build binary packages.")

# A list of files to include. These must be actual file names along with a
# complete path, starting from the current package directory. Directories
# are not allowed.
#
INCLUDE_FILES = []

LONG_DESCRIPTION = ""

# Python 2.x doesn't honour the 'package_dir' and 'package_data' arguments to
# setup() when building an 'sdist'. Generate MANIFEST.in containing the
# necessary files.
#
print("regenerating MANIFEST.in for Python 2.x")
MANIFEST = open("MANIFEST.in", "wt")
MANIFEST.write("include COPYING\n")
MANIFEST.close()

# Warn about symlinks
#
for file in INCLUDE_FILES:
    if os.path.islink(file):
        print("WARNING: '{0}' is a symbolic link. Please make sure that it refers to an absolute path.".format(file))

# Compute pairs of (destdir, [file, ...]) for the setup(data_files = ...) option
# from INCLUDE_FILES.
#
# Files will be installed in <prefix>/share/PACKAGE/ by `setup.py install`.
#
DATA_FILES = {}

for path in INCLUDE_FILES:

    target_dir = os.path.join("share", PACKAGE, os.path.dirname(path))

    if target_dir in DATA_FILES.keys():

        DATA_FILES[target_dir].append(path)

    else:
        DATA_FILES[target_dir] = [path]

# For most operations, cx_Freeze.setup() is a wrapper for distutils.core.setup().
#
# DATA_FILES.items() returns a list of (directory, [file, ...]) tuples as
# expected by setup().
#
# The syntax for the "include_files" option to "build_exe" is [(src, target), ...]
#
setup(name = PACKAGE,
      version = pycms.VERSION,
      author = "Florian Berger",
      author_email = "fberger@florian-berger.de",
      url = "http://florian-berger.de/en/software/pycms",
      description = PACKAGE + " - DESCRIPTION HERE",
      long_description = LONG_DESCRIPTION,
      license = "GPL",
      py_modules = [PACKAGE],
      packages = [],
      requires = [],
      provides = [PACKAGE],
      scripts = SCRIPTS,
      data_files = DATA_FILES.items(),
      executables = EXECUTABLES,
      options = {"build_exe" :
                 {"include_files" : INCLUDE_FILES}
                })

