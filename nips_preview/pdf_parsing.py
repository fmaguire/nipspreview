#!/usr/bin/env python3
# -*_ coding: utf-8 -*-
"""
Code for parsing pdfs using imagemagick
"""

import os
import tqdm
from string import punctuation
from operator import itemgetter
import re
import pickle
from stop_words import get_stop_words


def pdf_to_words(data, data_dir):
    """
    go over all pdfs in NIPS, get all the words from each, discard stop words,
    count frequencies of all words, retain top 100 for each PDF and dump a
    pickle of results into topwords.pkl

    also dump word lists of words ocurring more than 3 times to file
    """

    N = 100 # how many top words to retain

    # load in stopwords (i.e. boring words, these we will ignore)
    stopwords = get_stop_words('en')

    # go over every PDF, use pdftotext to get all words, discard boring ones, and count frequencies
    new_data = {} # dict of paperid -> [(word, frequency),...]
    word_list = []
    for paper_id, info in tqdm.tqdm(data.items(), desc="Parsing PDF for topwords"):

    	# create text file
        tmp = "out.txt"
        cmd = "pdftotext {} {}".format(info['pdf_path'], tmp)
        os.system(cmd)

        with open(tmp) as fh:
            # get all words in a giant list
            txtlst = fh.read().split()

            # take only alphanumerics
            words = [x.lower() for x in txtlst if re.match('^[\w-]+$', x) is not None]

            # remove stopwords
            words = [x for x in words if len(x)>2 and (not x in stopwords)]

        os.remove(tmp)

    	# count up frequencies of all words
        wcount = {}
        for w in words:
            wcount[w] = wcount.get(w, 0) + 1

        # sort and take top N
        top = sorted(wcount.items(), key=itemgetter(1), reverse=True)[:N]

        # only take words that occur at least a bit (for efficiency)
        words = [x for x in words if wcount[x] >= 3]
        word_list.append(words)

        # save to our dict
        info.update({'top_words': top})
        new_data.update({paper_id: info})

    # dump text to file for lda
    with open(os.path.join(data_dir, 'text_corpus.txt'), 'w') as fh:
        for words in word_list:
            fh.write(" ".join(words) + '\n')

    return new_data, word_list


def pdf_to_thumbnails(data, thumbnail_dir):
    """
    Build thumbnails
    """

    new_data = {}

    for paper_id, info in tqdm.tqdm(data.items(), desc="Building thumbnails"):
        # this is a mouthful...
        # take first 8 pages of the pdf ([0-7]), since 9th page are references
        # tile them horizontally, use JPEG compression 80, trim the borders for each image

        thumb_path = os.path.join(thumbnail_dir, paper_id + ".jpg")
        cmd = "montage {}[0-7] \
                -mode Concatenate \
                -tile x1 \
                -quality 80 \
                -resize x230 \
                -trim {}".format(info['pdf_path'],
                                 thumb_path)

        os.system(cmd)

        # add thumbnail paths to data
        info.update({'thumb_path': thumb_path})
        new_data.update({paper_id: info})

    return new_data

