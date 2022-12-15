# ----------------------------------------------------------------------
# |
# |  Element.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-14 10:00:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Element object"""

from dataclasses import dataclass

from SimpleSchema.Schema.Impl.Common.Range import Range


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Element(object):
    """Root of all entities produced during the parsing process"""

    # ----------------------------------------------------------------------
    range: Range
