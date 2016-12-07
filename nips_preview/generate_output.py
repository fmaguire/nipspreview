#!/usr/bin/env python3
"""
creates the nice .html page
"""

import pickle

from nips_preview import template

from numpy import argmax, zeros, ones
from math import log
import os

def build_html(data, project_dirs):

    lda_path = os.path.join(project_dirs['data'], 'ldaphi.pkl')
    with open(lda_path, 'rb') as fh:
        (ldak, phi, voca) = pickle.load(fh)

    # invert dictionary
    wtoid = {}
    for i,w in enumerate(voca):
        wtoid[w] = i

    # compute pairwise distances between papers based on top words
    # using something similar to tfidf, but simpler. No vectors
    # will be normalized or otherwise harmed during this computation.
    # first compute inverse document frequency (idf)
    N = len(data)
    idf = {}
    for info in data.values():
        tw = info['top_words']
        ts = [x[0] for x in tw]
        for t in ts:
            idf[t] = idf.get(t, 0.0) + 1.0
    for t in idf:
        idf[t] = log(N/idf[t], 2)


    # computer weighted intersection
    ds = zeros((N, N))

    for idx, paper_data in enumerate(data.items()):
        tw = paper_data[1]['top_words']
        w = set([x[0] for x in tw])
        accum = 0.0

        for idx2, paper_data2 in enumerate(data.items()):
            if idx2 < idx:
                continue

            tw2 = paper_data2[1]['top_words']
            w2 = set([x[0] for x in tw2])

            winter = w.intersection(w2)
            score = sum([idf[x] for x in winter])
            ds[idx, idx2] = score
            ds[idx2, idx] = score

    # build up the string for html
    html = template.template(project_dirs['abstracts'])

    s = ""
    js = "ldadist=["
    js2 = "pairdists=["
    for pid, paper_data in enumerate(data.items()):

    	# pid goes 1...N, p are the keys, pointing to actual paper IDs as given by NIPS, ~1...1500 with gaps

    	# get title, author
        info = paper_data[1]
        title = info['title']
        authors = info['authors']
        top_words = info['top_words']
        thumbpath = info['thumb_path']
        url = info['url']


        # some top100 words may not have been computed during LDA so exclude them if
        # they aren't found in wtoid
        t = [x[0] for x in top_words if x[0] in wtoid]
        tid = [int(argmax(phi[:, wtoid[x]])) for x in t] # assign each word to class

        tcat = ""
        for k in range(ldak):
            ws = [x for i,x in enumerate(t) if tid[i]==k]
            tcat += '[<span class="t'+ str(k) + '">' + ", ".join(ws) + '</span>] '

        # count up the complete distribution for the entire document and build up
        # a javascript vector storing all this
        svec = zeros(ldak)
        for w in t:
            svec += phi[:, wtoid[w]]
        if svec.sum() == 0:
            svec = ones(ldak)/ldak;
        else:
            svec = svec / svec.sum() # normalize
        nums = [0 for k in range(ldak)]
        for k in range(ldak):
            nums[k] = "%.2f" % (float(svec[k]), )

        js += "[" + ",".join(nums) + "]"
        if not pid == len(data)-1:
            js += ","

        # dump similarities of this document to others
        scores = ["%.2f" % (float(ds[pid, i]),) for i in range(N)]
        js2 += "[" + ",".join(scores) + "]"
        if not pid == len(data)-1:
            js2 += ","

        s += """

        <div class="apaper" id="pid{0}">
        <div class="paperdesc">
            <span class="ts">{1}</span><br />
            <span class="as">{2}</span><br /><br />
        </div>
        <div class="dllinks">
            <a href="{3}">[pdf] </a>
            <span class="sim" id="sim{0}">[rank by tf-idf similarity to this]</span><br />
    		<span class="abstr" id="ab{4}">[abstract]</span>
    	</div>
    	<img src = "{5}" width=100%><br />
    	<div class = "abstrholder" id="abholder{4}"></div>
    	<span class="tt">{6}</span>
    	</div>

    	""".format(pid, title, ", ".join(authors), url, int(paper_data[0]),
                thumbpath, tcat)

    newhtml = html.replace("RESULTTABLE", s)

    js += "]"
    newhtml = newhtml.replace("LOADDISTS", js)

    js2 += "]"
    newhtml = newhtml.replace("PAIRDISTS", js2)

    with open("nips_lda.html", 'w') as fh:
        fh.write(newhtml)

