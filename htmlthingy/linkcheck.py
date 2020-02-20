"""Check links in HTML files."""

import glob
import os
import pathlib
import re

import bs4

from htmlthingy import progressbar


def run(htmldir):
    htmlfiles = list(map(str, pathlib.Path(htmldir).rglob('*.html')))
    valid_targets = set()
    links = {}      # {filename: linklist}

    for filename in progressbar(htmlfiles, "Checking links"):
        valid_targets.add(os.path.relpath(filename, htmldir))

        with open(filename, 'r', encoding='utf-8') as file:
            soup = bs4.BeautifulSoup(file.read(), 'html.parser')

        for element in soup.find_all():
            try:
                valid_targets.add(os.path.basename(filename) +
                                  '#' + element['id'])
            except KeyError:
                pass

        for link in soup.find_all('a'):
            try:
                href = link['href']
            except KeyError:
                continue
            if href.startswith(('http://', 'https://')):
                continue

            if href.startswith('#'):
                href = os.path.basename(filename) + href
            links.setdefault(filename, []).append(href)

    for filename, targets in links.items():
        for target in targets:
            if target not in valid_targets:
                print("linkcheck: %s contains an invalid link to %s"
                      % (filename, target))
