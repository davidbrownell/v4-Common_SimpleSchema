# ----------------------------------------------------------------------
# |
# |  Statement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 09:29:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Statement object"""

from dataclasses import dataclass

from SimpleSchema.Schema.Impl.Common.Element import Element


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Statement(Element):
    """Abstract base class for all statements"""

    pass
