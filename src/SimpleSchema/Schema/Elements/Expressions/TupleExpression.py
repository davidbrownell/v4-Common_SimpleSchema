# ----------------------------------------------------------------------
# |
# |  TupleExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 12:42:51
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleExpression object"""

from dataclasses import dataclass
from typing import cast, ClassVar

from Common_Foundation.Types import overridemethod

from .Expression import Element, Expression

from ....Common import Errors


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TupleExpression(Expression):
    """One or more expressions"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                     = "Tuple"

    value: list[Expression]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(TupleExpression, self).__post_init__()

        if not self.value:
            raise Errors.TupleExpressionNoExpressions.Create(self.range)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "value", cast(list[Element], self.value)
