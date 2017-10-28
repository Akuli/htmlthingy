__author__ = 'Akuli'
__copyright__ = 'Copyright (c) 2017 Akuli'
__license__ = 'MIT'
__version__ = '0.1.0'

from htmlthingy import tags
from htmlthingy._converter import MarkupConverter
from htmlthingy._run import Builder

import tqdm


def progressbar(filelist, message):
    length = max(50-len(message), 0)
    pbar = tqdm.tqdm(
        filelist, bar_format=('%s{postfix:%d.%d} |{bar}|'
                              % (message, length, length)))
    for file in pbar:
        pbar.set_postfix({'file': file})
        yield file
