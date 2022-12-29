# ----------------------------------------------------------------------
# |
# |  ParseItemStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-16 10:35:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseItemStatement object"""

from dataclasses import dataclass

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.Identifier import Identifier

from SimpleSchema.Schema.Elements.Statements.Statement import Statement

from SimpleSchema.Schema.Parse.ParseElements.Types.ParseType import ParseType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseItemStatement(Statement):
    """Defines a single item"""

    # ----------------------------------------------------------------------
    name: Identifier
    type: ParseType

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "name", self.name
        yield "type", self.type
