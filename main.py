#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runner Script for generating NIPS preview html"""

import sys
import os
import nips_preview
from nips_preview import utils


def main(args):
    """
    Script main subroutine
    """
    output_path = args[1]

    proceedings_html = args[2]

    # build project structure
    project = utils.build_dir_structure(output_path)

    # get source html page
    source_path = os.path.join(project['content'], "source.html")
    utils.get_source(proceedings_html, source_path)
    project.update({'source': source_path})

    print(project)


if __name__ == '__main__':

    main(sys.argv)




