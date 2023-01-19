# ----------------------------------------------------------------------
# |
# |  Visibility.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 20:50:10
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Visibility object"""

from enum import auto, Enum


# ----------------------------------------------------------------------
class Visibility(Enum):
    """Access restriction for a statement"""

    Public                                  = auto()
    Protected                               = auto()
    Private                                 = auto()
