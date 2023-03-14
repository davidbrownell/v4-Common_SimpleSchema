# ----------------------------------------------------------------------
# |
# |  ParseState.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-03-13 07:23:20
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseState object"""

from dataclasses import dataclass


# ----------------------------------------------------------------------
@dataclass
class ParseState(object):
    """Information maintained throughout the parsing process"""

    pass # Nothing here so far
