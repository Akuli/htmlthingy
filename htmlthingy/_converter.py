import re
import textwrap

from htmlthingy import tags


class MarkupConverter:
    """Convert markup into HTML.

    This class uses regular expressions and functions from
    :mod:`htmlthingy.tags`, but you can easily customize it with custom
    regexes and callbacks.

    Example:

    >>> markup = '''
    ... # Hello World!
    ...
    ... ## Subtitle
    ...
    ... **Bold**, *italic*, _underline_, ``some code``
    ...
    ... (some-id)
    ... Blah blah blah.
    ... '''
    >>> print(''.join(MarkupConverter().convert(markup)))
    <h1 id="hello-world">Hello World!</h1>
    <h2 id="subtitle">Subtitle</h2>
    <p><b>Bold</b>, <i>italic</i>, <u>underline</u>, <code>some code</code>
    </p>
    <p id="some-id">Blah blah blah.
    </p>
    """

    def __init__(self):
        self.pygments_style = 'default'
        self._inliners = {}
        self._multiliners = {}
        self._add_basic_stuff()

    def convert(self, string, filename='<string>'):
        """Produce output from an input string.

        The *filename* will be used as an argument to callbacks, so they
        can do different things depending on which file is processed.
        Usually it's a relative path to a ``.txt`` input file with
        :data:`os.sep` replaced by ``'/'``.

        This yields pieces of the final string that are supposed to be
        joined together. You can do e.g. this::

            with open('input.rst', 'r', encoding='utf-8') as file:
                markup = file.read()

            with open('output.html', 'w', encoding='utf-8') as file:
                for chunk in MarkupConverter().convert(content):
                    file.write(chunk)

        Use ``''.join(converter.convert(contents))`` if you want the
        output as a string.
        """
        for chunk in re.split(r'\n\n(?=\S)', string):
            matches = {regex.search(chunk.strip('\n') + '\n')
                       for regex in self._multiliners} - {None}
            if len(matches) > 1:
                # TODO: better error
                raise ValueError(f"ambiguous markup in {filename}\n\n{chunk}")

            if matches:
                [match] = matches
                yield from self._multiliners[match.re](match, filename)
            elif chunk.strip():
                yield '<p>'
                yield from self.convert_chunk(chunk, filename)
                yield '</p>\n\n'

    def convert_chunk(self, chunk, filename):
        """
        Like :meth:`convert`, but doesn't handle multi-line things (e.g.
        titles and code blocks).

        Use this instead of :meth:`convert` if you want to parse nested
        markup, like ``**a [link](something) inside bold**``.
        """
        while chunk:
            matches = {regex.search(chunk)
                       for regex in self._inliners} - {None}
            if not matches:
                yield chunk
                break

            min_start = min(m.start() for m in matches)
            firsts = [m for m in matches if m.start() == min_start]
            if len(firsts) > 1:
                # TODO: better error
                raise ValueError(f"ambiguous markup in {filename}\n\n{chunk[min_start:]}")

            match = firsts[0]
            yield chunk[:min_start]
            yield self._inliners[match.re](match, filename)
            chunk = chunk[match.end():]

    def add_inliner(self, regex):
        """Add a new non-multiline processor function.

        Use this as a decorator, like this::

            @converter.add_inliner(r'``(.+?)``')
            def code(match, filename):
                return '<code>' + match.group(1) + '</code>'

        The regex can be a string or a compiled regex from
        :func:`re.compile`. Use a compiled regex if you want to use
        regex flags.

        The ``filename`` is a name of the HTML output file, with
        :data:`os.sep` replaced with ``'/'``.
        """
        if isinstance(regex, str):
            regex = re.compile(regex)

        def inner(function):
            self._inliners[regex] = function
            return function

        return inner

    def add_multiliner(self, regex):
        """Add a new multi-line processor function.

        The function should return a three-tuple
        ``(prefix, content, suffix)`` where ``content`` will be
        processed normally, and it will be inserted between ``prefix``
        and ``suffix``.

        .. TODO: explain more, show decorator usage, add an example
        """
        if isinstance(regex, str):
            regex = re.compile(regex)

        def inner(function):
            self._multiliners[regex] = function
            return function

        return inner

    def _add_basic_stuff(self):
        @self.add_multiliner(r'^(#{1,5})\s*(.*)$')
        def title_handler(match, filename):
            content = ''.join(self.convert_chunk(match.group(2), filename))
            yield tags.title(content, len(match.group(1)))

        @self.add_multiliner(r'^\(([\w-]+)\)\n')
        def id_adder(match, filename):
            markup = match.string[match.end():]
            assert markup, "blank line after (...)"
            content = ''.join(self.convert(markup, filename)).lstrip()

            regex = re.compile(r'^<(\w+)')      # fuck stackoverflow
            assert regex.search(content) is not None, "cannot use (...) here"
            yield regex.sub(r'<\1 id="%s"' % match.group(1), content, count=1)

        @self.add_multiliner(r'^indent:\n')
        def indent_handler(match, filename):
            markup = textwrap.dedent(match.string[match.end():])
            assert markup, "blank line after 'indent:'"
            yield '<div class="indent">'
            yield from self.convert(markup, filename)
            yield '</div>'

        # prevent adding a <p> tag
        @self.add_multiliner(r'^noparagraph:\n')
        def no_paragraph_handler(match, filename):
            markup = textwrap.dedent(match.string[match.end():])
            assert markup, "blank line after 'noparagraph:'"
            yield from self.convert(markup, filename)

        @self.add_multiliner(r'^(gray|red)box:(.*)\n')
        def box_handler(match, filename):
            content = textwrap.dedent(match.string[match.end():])
            yield '<div class="box %sbox">' % match.group(1)
            if match.group(2).strip():
                yield '<h2>'
                yield from self.convert_chunk(match.group(2), filename)
                yield '</h2>'
            yield from self.convert(content, filename)
            yield '</div>'

        @self.add_multiliner(r'^floatingbox:(.*)\n')
        def floating_box_handler(match, filename):
            content = textwrap.dedent(match.string[match.end():])
            yield '<div class="floatingbox">'
            if match.group(1).strip():
                yield '<h2>'
                yield from self.convert_chunk(match.group(1), filename)
                yield '</h2>'
            yield from self.convert(content, filename)
            yield '</div>'

        @self.add_multiliner(r'^image:\s*(\S.*)\n')
        def image_handler(match, filename):
            css = match.string[match.end():]
            yield tags.image(match.group(1), css.replace('\n', ' '))

        @self.add_multiliner(r'^comment:')
        def do_nothing(match, filename):
            if False:
                yield

        @self.add_multiliner(r'^code:(.*)\n')
        def code_handler(match, filename):
            code = textwrap.dedent(match.string[match.end():])
            yield tags.multiline_code(code, match.group(1).strip() or 'text',
                                      self.pygments_style)

        @self.add_multiliner(r'^\* ')
        def list_handler(match, filename):
            yield '<ul>'
            for item in re.split(r'\n\* ', match.string[match.end():]):
                yield '<li>'
                yield from self.convert_chunk(item, filename)
                yield '</li>'
            yield '</ul>'

        @self.add_multiliner(r'^1\. ')
        def numbered_list_handler(match, filename):
            yield '<ol>'
            for item in re.split(r'\n\d\. ', match.string[match.end():]):
                yield '<li>'
                yield from self.convert_chunk(item, filename)
                yield '</li>'
            yield '</ol>'

        @self.add_inliner(r'\B\*\*(.+?)\*\*\B')
        def bold_handler(match, filename):
            content = ''.join(self.convert_chunk(match.group(1), filename))
            return tags.bold(content)

        @self.add_inliner(r'\B\*([^\*].*?)\*\B')
        def italic_handler(match, filename):
            content = ''.join(self.convert_chunk(match.group(1), filename))
            return tags.italic(content)

        @self.add_inliner(r'\b_(.+?)_\b')
        def underline_handler(match, filename):
            content = ''.join(self.convert_chunk(match.group(1), filename))
            return tags.underline(content)

        @self.add_inliner(r'``(.+?)``')
        def inline_code_handler(match, filename):
            return tags.inline_code(match.group(1))

        @self.add_inliner(r'\[([\S\s]+?)\]\((.+?)\)')
        def link_handler(match, filename):
            content = ''.join(self.convert_chunk(match.group(1), filename))
            return tags.link(content, match.group(2))

        @self.add_inliner(r'\s--\s')
        def en_dash(match, filename):
            return ' \N{EN DASH} '


if __name__ == '__main__':
    import doctest
    print(doctest.testmod())
