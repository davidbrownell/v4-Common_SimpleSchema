# ----------------------------------------------------------------------
# |
# |  ParseItemStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 10:41:38
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseItemStatement object"""

from dataclasses import dataclass

from Common_Foundation.Types import overridemethod

from ..Common.ParseIdentifier import ParseIdentifier
from ..Types.ParseType import ParseType

from .....Elements.Statements.Statement import Element, Statement


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseItemStatement(Statement):
    """Defines a single item; instances are only valid during the parsing process and are converted to other items in subsequent steps."""

    # ----------------------------------------------------------------------
    name: ParseIdentifier
    type: ParseType

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "name", self.name
        yield "type", self.type
