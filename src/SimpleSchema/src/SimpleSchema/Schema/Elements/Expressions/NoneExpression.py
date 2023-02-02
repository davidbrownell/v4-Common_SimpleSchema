# ----------------------------------------------------------------------
# |
# |  NoneExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 12:33:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NoneExpression object"""

from dataclasses import dataclass
from types import NoneType
from typing import ClassVar

from .Expression import Expression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NoneExpression(Expression):
    """None value"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                     = "None"

    value: NoneType                         = None
