"""Functions that output bits of HTML like ``'<h1>Hello World</h1>'``."""

import re

import pygments.formatters
import pygments.lexers


def _id_ify(string):
    r"""
    >>> _id_ify("Hello There!")
    'hello-there'
    >>> _id_ify("??\t???!?!?!?!??????????")
    '3f3f093f3f'
    """ 
    nice_id = re.sub('[\W_]','-', string).strip('-').lower()
    if nice_id:
        return nice_id
    return ''.join(map('{:02x}'.format, string.encode('utf-8')))[:10]


def title(content, level=1):
    """Corresponds to ``### content`` in the markup.

    :param content: HTML that will go inside the tags.
    :param level: number of ``#``'s in the markup.

    >>> title('Hello World!')
    '<h1 id="hello-world">Hello World!</h1>'
    >>> title('Subtitle', 2)
    '<h2 id="subtitle">Subtitle</h2>'
    >>> title('WTF?!', 3)
    '<h3 id="wtf">WTF?!</h3>'
    """
    return ('<h{level} id="{id}">{}'
            '<a class="headerlink" href="#{id}" '
            'title="Link to this title">\N{PILCROW SIGN}</a>'
            '</h{level}>').format(content, id=_id_ify(content), level=level)


def link(content, target):
    """Corresponds to ``[content](target)`` in the markup.

    :param content: HTML that will go inside the tags.
    :param target: a full URL, or a local ``filename.html#subtitle`` URL
    """
    return '<a href="%s">%s</a>' % (target, content)


def image(url, style=''):
    """Corresponds to ``image: url`` in the markup.

    :param url: a full URL or a ``/``-separated path to an image file.
    :param style: CSS for this image, e.g. ``'float: right;'``. Below \
                  ``image: url`` in the markup.
    """
    return '<img src="%s" style="%s" />' % (url, style)


def bold(content):
    """Corresponds to ``**content**`` in the markup.

    :param content: HTML that will go inside the tags.

    >>> 'i said be ' + bold('careful')
    'i said be <b>careful</b>'
    """
    return '<b>' + content + '</b>'


def italic(content):
    """Corresponds to ``*content*`` in the markup.

    :param content: HTML that will go inside the tags.

    >>> 'i would ' + italic('really') + ' like to see that'
    'i would <i>really</i> like to see that'
    """
    return '<i>' + content + '</i>'


def underline(content):
    """Corresponds to ``_text_`` in the markup.

    :param content: HTML that will go inside the tags.

    >>> 'i said ' + underline('do it')
    'i said <u>do it</u>'
    """
    return '<u>' + content + '</u>'


def inline_code(code):
    r"""Corresponds to ``\`\`code\`\``` in the markup.

    :param text: the code string as plain text, not HTML.

    >>> 'type ' + inline_code('print("hello world")') + ' and press enter'
    'type <code>print("hello world")</code> and press enter'
    """
    return '<code>' + code + '</code>'


def multiline_code(code, lexer_name, pygments_style):
    """Create HTML that displays highlighted code with Pygments.

    The HTML is wrapped in a ``<div>`` with ``class="highlight"``.

    :param code: the code string as plain text, not HTML.
    :param lexer_name: "short name" of a Pygments lexer, see `this list\
 of lexers <http://pygments.org/docs/lexers/>`_.
    :param pygments_style: name of a Pygments style, see `this style ex\
ample page <https://help.farbox.com/pygments.html>`_.

    There's no example because the HTML created by Pygments looks kind
    of messy when viewed as plain text.
    """
    lexer = pygments.lexers.get_lexer_by_name(lexer_name)
    formatter = pygments.formatters.HtmlFormatter(
        style=pygments_style, noclasses=True)
    return pygments.highlight(code, lexer, formatter)
