#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runner Script for generating NIPS preview html"""

import sys
import os
import nips_preview
from nips_preview import utils
from nips_preview import scrape
from nips_preview import pdf_parsing
from nips_preview import lda
from nips_preview import generate_output



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

    # get topwords
    top_words = pdf_parsing.pdf_to_words(data)

    # generate thumbnails
    data = pdf_parsing.pdf_to_thumbnail(data)

    # create corpus
    # all_papers =

    # perform LDA
    #lda lda.

    # generate html
    #generate_output.xxxx




if __name__ == '__main__':

    main(sys.argv)




