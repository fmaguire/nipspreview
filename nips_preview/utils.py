#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility function to generate NIPS preview"""

import os
import sys

import urllib.request

def build_dir_structure(path):
    """
    Build directory structure for web page
    """

    try:
        os.mkdir(path)
    except FileExistsError:
        print("Directory Already Exists")
        print("Proceeding")

    directories = {'base': path}

    for subdir in ["data", "content", "abstracts", "thumbs", "js"]:
        subpath = os.path.join(path, subdir)
        try:
            os.mkdir(subpath)
        except FileExistsError:
            pass
        directories.update({subdir: subpath})

    return directories


def get_source(html, output_path):
    """
    Fetch html into output file
    """

    with urllib.request.urlopen(html) as response:
        source = response.read()

    with open(output_path, 'wb') as out_fh:
        out_fh.write(source)

