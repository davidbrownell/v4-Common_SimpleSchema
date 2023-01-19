# ----------------------------------------------------------------------
# |
# |  Statement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 12:00:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Statement object"""

from dataclasses import dataclass

from ...Common.Element import Element


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Statement(Element):
    """Abstract base class for all statements"""

    pass
