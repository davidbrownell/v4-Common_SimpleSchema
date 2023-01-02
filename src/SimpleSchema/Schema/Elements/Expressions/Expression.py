# ----------------------------------------------------------------------
# |
# |  Expression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 09:33:13
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Expression object"""

from dataclasses import dataclass

from SimpleSchema.Schema.Elements.Common.Element import Element


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Expression(Element):
    """Abstract base class for all expressions"""

    pass
