# -*- coding: utf-8 -*-

import os

folderpath = os.path.dirname(__file__)
files = os.listdir(folderpath)
files = [os.path.join(folderpath, f) for f in files if f.endswith(".py")]

def add_encoding_header(filepath):
    with open(filepath, "r") as fi:
        lines = fi.readlines()
    if not lines[0].startswith("# -*- coding: utf-8 -*-"):
        lines.insert(0, "# -*- coding: utf-8 -*-\r")

    with open(filepath, "w") as fi:
        fi.writelines(lines)
        


for x in files:
    print x