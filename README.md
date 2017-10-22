# HTML Thingy

This thingy creates HTML from non-standard, Markdown-like and highly
customizable markup. All you need to create a static website with this thingy
is some Python and CSS experience. If you want to add custom syntax, experience
with regular expressions is also required (but `help('re')` is your friend).

I created this thing because originally [my math
tutorial](https://akuli.github.io/math-tutorial) was done with Sphinx, but
writing sphinx plugins was really difficult. The plugin API is huge and not
very well documented (which is kind of surprising, considering that Sphinx is
mostly a documentation tool). Writing new Sphinx plugins took many hours, and
even a simple thing is lots of boilerplate code.

## Installation

Windows:

    py -m pip install --user https://github.com/Akuli/htmlthingy/archive/master.zip

Other systems:

    python3 -m pip install --user https://github.com/Akuli/htmlthingy/archive/master.zip

## Hello World!

**index.txt**:

```
# Hello World!

This is a test.
```

**build.py**:

```python
import htmlthingy

builder = htmlthingy.Builder()
builder.run()
```

Run `build.py` with Python 3.4 or newer, and open `html/index.html` in your
favorite browser. It's minimal because we didn't do any CSS styling yet, but
we'll fix that in a moment.

## Default Syntax

This file demonstrates most of the features available by default.

**syntaxtest.txt**:

```
# Main Title

Blah blah blah. **Bold**, *italic*, _underline_, ``some code``.

## Subtitle

comment: One line comment.

comment: Multi-line comment.
    Comments can be more than one line long.

    This is still a part of the comment.

code: python3
    print("Hello World!")

    print("This is still a part of the code.")

### Subsubtitle

Subtitles are supported to at most 5 ``#`` characters.

[This](index.html) is a link to our other file, and [this](#subtitle) is a link
to a title in this file.

(thing)
This section can be referred to as ``syntaxtest.html#thing``.

<small>The markup may contain any HTML.</small>

comment: TODO: show an image and aligning them
```

Run `build.py` again and open `html/syntaxtest.html`.

## Custom Syntax

This is probably my favorite part about this whole thingy. Let's create a new
build file and try it out.

**build.py**:

```python
import htmlthingy


builder = htmlthingy.Builder()

@builder.converter.add_inliner(r'\B--(.+?)--\B')
def uppercase(match, filename):
    return '<b>%s!!!</b>' % match.group(1).upper()

builder.run()
```

**uppertest.txt**:

```
# Uppercase Test

--hello world--
```

Run `build.py` again and open `html/uppertest.html`.

## More stuff

There are many more things to be documented. I'll write more about them later.
