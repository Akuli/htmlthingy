import functools
import glob
import os
import posixpath
import shutil
import string

import tqdm

from htmlthingy import MarkupConverter


simple_tqdm = functools.partial(tqdm.tqdm, bar_format=(
    '{desc:35} |{bar}| {n_fmt}/{total_fmt}, {percentage:3.0f}%'))


class Builder:

    def __init__(self, title=None):
        self.converter = MarkupConverter()
        self.infiles = sorted(glob.glob('*.txt'))
        self.outputdir = 'html'
        self.additional_files = glob.glob('*.css') + glob.glob('*.js')

    def infile2outfile(self, txtfile):
        """Return a HTML file path based on a text file path."""
        assert not os.path.isabs(txtfile), (
            "expected relative path, got '%s'" % txtfile)
        basename_ish = os.path.splitext(txtfile)[0] + '.html'  # may contain /
        result = os.path.join(self.outputdir, basename_ish)
        return result.replace(os.sep, '/')

    def run(self):
        # TODO: cache stuff somehow
        if os.path.exists(self.outputdir):
            shutil.rmtree(self.outputdir)
        os.makedirs(self.outputdir)

        pbar = simple_tqdm(self.infiles, desc="Processing text files...")
        for txtfile in pbar:
            pbar.set_postfix({'file': txtfile})

            with open(txtfile, 'r', encoding='utf-8') as file:
                content = file.read()

            with open(self.infile2outfile(txtfile), 'x',
                      encoding='utf-8') as file:
                file.write('<!DOCTYPE html>\n')
                file.write('<html>\n')

                file.write('<head>\n')
                file.write('<meta charset="UTF-8">\n')
                if 'style.css' in self.additional_files:
                    copied_path = os.path.join(self.outputdir, 'style.css')
                    relative = os.path.relpath(
                        copied_path,
                        os.path.dirname(self.infile2outfile(txtfile)))
                    file.write('<link rel="stylesheet" href="%s">\n'
                               % relative.replace(os.sep, '/'))
                file.write('<title>%s</title>\n' % self.get_title(txtfile))
                file.write(self.get_head_extras(txtfile))
                file.write('</head>\n')

                file.write('<body>\n')

                file.write('<div id="content">\n')
                for chunk in self.converter.convert(content):
                    file.write(chunk)
                file.write('</div>\n')

                sidebar = self.get_sidebar_content(txtfile)
                if sidebar is not None:
                    file.write('<div id="sidebar">%s</div>\n' % sidebar)

                file.write('</body>\n')
                file.write('</html>\n')

        if self.additional_files:
            pbar = simple_tqdm(self.additional_files,
                               desc="Copying additional files...")
            for source in pbar:
                pbar.set_postfix({'file': source})

                dest = os.path.join(self.outputdir, source)
                if os.path.isdir(source):
                    shutil.copytree(source, dest)
                else:
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    shutil.copy(source, dest)

    # rest of these are meant to be monkey-patched
    def get_title(self, txtfile):
        # this is lol
        with open(txtfile, 'r', encoding='utf-8') as file:
            firstline = file.readline()
        return firstline.strip(string.whitespace + string.punctuation)

    def get_head_extras(self, txtfile):
        return ''

    def get_sidebar_content(self, txtfile):
        return None
