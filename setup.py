import os

if os.path.exists("paver-minilib.zip"):
    import sys

    sys.path.insert(0, "paver-minilib.zip")

import paver.command

paver.command.main()

