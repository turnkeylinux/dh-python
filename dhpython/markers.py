# Copyright © 2022 Stefano Rivera <stefanor@debian.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Handle Environment Markers
https://www.python.org/dev/peps/pep-0508/#environment-markers

TODO: Ideally replace with the packaging library, but the API is currently
private: https://github.com/pypa/packaging/issues/496
"""

import re


SIMPLE_ENV_MARKER_RE = re.compile(r'''
    (?P<marker>[a-z_]+)
    \s*
    (?P<op><=?|>=?|[=!~]=|===)
    \s*
    (?P<quote>['"])
    (?P<value>.*)  # Could contain additional markers
    (?P=quote)
    ''', re.VERBOSE)
COMPLEX_ENV_MARKER_RE = re.compile(r'''
    (?:\s|\))
    (?:and|or)
    (?:\s|\()
    ''', re.VERBOSE)


class ComplexEnvironmentMarker(Exception):
    pass


def parse_environment_marker(marker):
    """Parse a simple marker of <= 1 environment restriction"""
    marker = marker.strip()
    if marker.startswith('(') and marker.endswith(')'):
        marker = marker[1:-1].strip()

    m = COMPLEX_ENV_MARKER_RE.search(marker)
    if m:
        raise ComplexEnvironmentMarker()

    m = SIMPLE_ENV_MARKER_RE.match(marker)
    if not m:
        raise ComplexEnvironmentMarker()

    return (
        m.group('marker'),
        m.group('op'),
        m.group('value'),
    )
