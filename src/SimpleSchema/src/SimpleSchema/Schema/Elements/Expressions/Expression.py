# ----------------------------------------------------------------------
# |
# |  Expression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 09:48:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Expression object"""

from dataclasses import dataclass
from typing import Any, ClassVar

from ..Common.Element import Element


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Expression(Element):
    """Abstract base class for all expressions"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                     = ""

    value: Any

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.NAME != "", "Make sure to define the expression's name."
