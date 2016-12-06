#!/usr/bin/env python3
"""
creates the nice .html page
"""

import pickle

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
    for paper_id, info in data.items():
        tw = info['top_words']
        ts = [x[0] for x in tw]
        for t in ts:
            idf[t] = idf.get(t, 0.0) + 1.0
    for t in idf:
        idf[t] = log(N/idf[t], 2)


    # computer weighted intersection
    ds = zeros((N, N))

    for idx, paper_id, info in enumerate(data.items()):
        tw = info['top_words']
        w = set([x[0] for x in tw])
        accum = 0.0

        for idx2, paper_id2, info2 in enumerate(data.items()):
            if idx2 < idx:
                continue

            tw2 = info2['top_words']
            w2 = set([x[0] for x in tw2])

            winter = w.intersection(w2)
            score = sum([idf[x] for x in winter])
            ds[idx, idx2] = score
            ds[idx2, idx] = score

    # build up the string for html
    template = os.path.join(project_dirs['data'], "nips_template.html")
    with open(template) as fh:
        html = fh.read()

    s = ""
    js = "ldadist=["
    js2 = "pairdists=["
    for pid, paper_id, info in enumerate(data.items()):

    	# pid goes 1...N, p are the keys, pointing to actual paper IDs as given by NIPS, ~1...1500 with gaps

    	# get title, author
        title = info['title']
        authors = info['authors']
        top_words = info['top_words']
        thumbpath = info['thumb_path']
        pdfpath = info['pdf_path']

        # some top100 words may not have been computed during LDA so exclude them if
        # they aren't found in wtoid
        t = [x[0] for x in topwords if x[0] in wtoid]
        tid = [int(argmax(phi[:, wtoid[x]])) for x in t] # assign each word to class

        tcat = ""
        for k in range(ldak):
            ws = [x for i,x in enumerate(t) if tid[i]==k]
            tcat += '[<span class="t'+ k + '">' + ", ".join(ws) + '</span>] '

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

        <div class="apaper" id="pid%d">
        <div class="paperdesc">
            <span class="ts">%s</span><br />
            <span class="as">%s</span><br /><br />
        </div>
        <div class="dllinks">
            <a href="%s">[pdf] </a>
            <span class="sim" id="sim%d">[rank by tf-idf similarity to this]</span><br />
    		<span class="abstr" id="ab%d">[abstract]</span>
    	</div>
    	<img src = "%s"><br />
    	<div class = "abstrholder" id="abholder%d"></div>
    	<span class="tt">%s</span>
    	</div>

    	""" % (pid, title, " ".join(authors), pdfpath, pid, int(paper_id), thumbpath, int(paper_id), tcat)


    newhtml = html.replace("RESULTTABLE", s)

    js += "]"
    newhtml = newhtml.replace("LOADDISTS", js)

    js2 += "]"
    newhtml = newhtml.replace("PAIRDISTS", js2)

    with open("nips_lda.html", 'w') as fh:
        fh.write(newhtml)

