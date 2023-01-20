# ----------------------------------------------------------------------
# |
# |  ListExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 12:53:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ListExpression object"""

from dataclasses import dataclass
from typing import cast, ClassVar

from Common_Foundation.Types import overridemethod

from .Expression import Element, Expression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ListExpression(Expression):
    """A list of expressions"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                     = "List"

    value: list[Expression]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "value", cast(list[Element], self.value)
