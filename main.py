#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runner Script for generating NIPS preview html"""

import sys
import os
import pickle
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

    # scrape pdfs using the existence of papers.pkl as a marker
    # to check if this is necessary
    data = scrape.parse_html(proceedings_html, project['data'],
                             project['abstracts'])

    ## get topwords and texts
    data = pdf_parsing.pdf_to_words(data, project['data'])

    ## generate thumbnails
    data = pdf_parsing.pdf_to_thumbnails(data, project['thumbs'])

    with open(os.path.join(project['data'], 'papers.pkl'), 'wb') as fh:
        pickle.dump(data, fh)


    lda.run_lda(os.path.join(project['data'], "text_corpus.txt"),
                project['data'])


    with open(os.path.join(project['data'], 'papers.pkl'), 'rb') as fh:
        data = pickle.load(fh)

    # generate html
    generate_output.build_html(data, project)

if __name__ == '__main__':

    main(sys.argv)




