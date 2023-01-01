# ----------------------------------------------------------------------
# |
# |  TupleExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-30 08:56:57
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleExpression object"""

from dataclasses import dataclass
from typing import List

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Expressions.Expression import Expression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TupleExpression(Expression):
    """A tuple"""

    # ----------------------------------------------------------------------
    expressions: List[Expression]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.expressions:
            raise SimpleSchemaException("No expressions were provided.", self.range)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "expressions", self.expressions
