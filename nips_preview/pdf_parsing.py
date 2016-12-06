#!/usr/bin/env python3
# -*_ coding: utf-8 -*-
"""
Code for parsing pdfs using imagemagick
"""

import os
from string import punctuation
from operator import itemgetter
import re
import pickle


def pdf_to_words(data, data_dir):
    """
    go over all pdfs in NIPS, get all the words from each, discard stop words,
    count frequencies of all words, retain top 100 for each PDF and dump a
    pickle of results into topwords.p
    """

    N = 100 # how many top words to retain

    # load in stopwords (i.e. boring words, these we will ignore)
    with open("stopwords.txt") as fh:
        stopwords = fh.read().split()
        stopwords = [x.strip(punctuation) for x in stopwords if len(x)>2]


    # go over every PDF, use pdftotext to get all words, discard boring ones, and count frequencies
    top_dict = {} # dict of paperid -> [(word, frequency),...]
    for paper_id, info in data:

    	# create text file
        cmd = "pdftotext {} {}".format(info['pdf_path'], "out.txt")
        os.system(cmd)

        with open('out.txt') as fh:
            # get all words in a giant list
            txtlst = fh.read().split()

            # take only alphanumerics
            words = [x.lower() for x in txtlst if re.match('^[\w-]+$', x) is not None]

            # remove stopwords
            words = [x for x in words if len(x)>2 and (not x in stopwords)]

    	# count up frequencies of all words
        wcount = {}
        for w in words:
            wcount[w] = wcount.get(w, 0) + 1

        # sort and take top N
        top = sorted(wcount.iteritems(), key=itemgetter(1), reverse=True)[:N]

        # save to our dict
        top_dict[paper_id] = top

    # dump to pickle
    with open(os.path.join(data_dir, 'topwords.p'), 'wb') as fh:
        pickle.dump(top_dict, fh)


def pdf_to_thumbnails(data, thumbnail_dir):
    """
    Build thumbnails
    """

    for paper_id, info in data:
	    # this is a mouthful...
	    # take first 8 pages of the pdf ([0-7]), since 9th page are references
	    # tile them horizontally, use JPEG compression 80, trim the borders for each image
	    cmd = "montage {}[0-7] \
                    -mode Concatenate \
                    -tile x1 \
                    -quality 80 \
                    -resize x230 \
                    -trim {}".format(info['pdf_path'],
                                     thumbnail_dir + paper_id + ".jpg")
	    os.system(cmd)


