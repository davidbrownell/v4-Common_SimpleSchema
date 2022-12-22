# ----------------------------------------------------------------------
# |
# |  ListExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-16 09:36:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ListExpression object"""

from dataclasses import dataclass
from typing import List

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Expressions.Expression import Expression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ListExpression(Expression):
    """A list of expressions"""

    # ----------------------------------------------------------------------
    items: List[Expression]  # Can be an empty list

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "items", self.items
