#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runner Script for generating NIPS preview html"""

import sys
import os
import nips_preview
from nips_preview import utils
from nips_preview import scrape


def main(args):
    """
    Script main subroutine
    """
    output_path = args[1]

    proceedings_html = args[2]

    # build project structure
    project = utils.build_dir_structure(output_path)

    # get source html page
    data = scrape.parse_html(proceedings_html, project['data'])


if __name__ == '__main__':

    main(sys.argv)




