#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
submodule to scrape the html page for author details and grab
the papers
"""


from bs4 import BeautifulSoup
import pickle
import os
import urllib.request
import tqdm

def get_source(html):
    """
    Fetch html into output file
    """

    with urllib.request.urlopen(html) as response:
        source = response.read()

    return source

def parse_html(html, data_dir, abstract_dir):

    data = get_source(html)

    with open(os.path.join(data_dir, 'source.html'), 'wb') as fh:
        fh.write(data)

    soup = BeautifulSoup(data, 'html.parser')

    papers = {}

    # only look at the main-container div
    for main in soup.find_all('div', class_='main-container'):
        for paper in tqdm.tqdm(main.find_all('li'), desc="Scraping Papers"):
            title = paper.a.get_text()
            #url = "/".join(html.split('/')[:3]) + paper.a['href']
            url = "http://papers.nips.cc/" + paper.a['href']
            paper_id = paper.a['href'].split('/')[2].split('-')[0]
            authors = [x.get_text() for x in paper.find_all('a', class_='author')]

            # skip papers without author information
            if len(authors) == 0:
                continue

            # get pdf
            # print("Scraping: {}".format(title))
            pdf = get_source(url + ".pdf")
            pdf_path = os.path.join(data_dir, url.split('/')[-1] + ".pdf")

            with open(pdf_path, 'wb') as fh:
                fh.write(pdf)

            # get abstract
            paper_html = get_source(url)
            paper_soup = BeautifulSoup(paper_html, 'html.parser')
            abstract = paper_soup.find('p', class_='abstract').get_text()

            abstract_path = os.path.join(abstract_dir, paper_id) + '.txt'

            with open(abstract_path, 'w') as fh:
                fh.write(abstract)

            papers.update({paper_id: {'title': title,
                                      'authors': authors,
                                      'abstract_path': abstract_path,
                                      'url': url,
                                      'pdf_path': pdf_path}})

    with open(os.path.join(data_dir, 'papers.pkl'), 'wb') as fh:
        pickle.dump(papers, fh)

    return papers
