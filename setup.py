import os
import re
import sys

from setuptools import setup, find_packages


assert sys.version_info >= (3, 4), "use Python 3.4 or newer"


def get_requirements():
    with open('requirements.txt', 'r') as file:
        for line in map(str.strip, file):
            if (not line.startswith('#')) and line:
                yield line


def find_metadata():
    with open(os.path.join('htmlthingy', '__init__.py')) as file:
        content = file.read()

    result = dict(re.findall(
        r'''^__(author|copyright|license|version)__ = ['"](.*)['"]$''',
        content, re.MULTILINE))
    assert result.keys() == {'author', 'copyright', 'license', 'version'}

    return result


setup(
    name='htmlthingy',
    description="Simple, extensible and non-standard markup to HTML converter",
    url='https://github.com/Akuli/htmlthingy',
    install_requires=list(get_requirements()),
    packages=find_packages(),
    **find_metadata()       # must not end with , before python 3.5
)
