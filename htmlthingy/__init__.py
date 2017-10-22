__author__ = 'Akuli'
__copyright__ = 'Copyright (c) 2017 Akuli'
__license__ = 'MIT'
__version__ = '0.1.0'

from htmlthingy import tags
from htmlthingy._converter import MarkupConverter
from htmlthingy._run import Builder

import tqdm


def _truncate(filename):
    if len(filename) <= 15:
        return filename
    return filename[:12] + '...'


def progressbar(filelist, message):
    pbar = tqdm.tqdm(
        filelist, desc=message,
        bar_format='{desc:24}|{bar}| {n_fmt}/{total_fmt}{postfix:22}')
    for file in pbar:
        pbar.set_postfix({'file': _truncate(file)})
        yield file
