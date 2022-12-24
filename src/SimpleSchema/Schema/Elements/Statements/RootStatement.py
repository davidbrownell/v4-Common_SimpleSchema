# ----------------------------------------------------------------------
# |
# |  RootStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 09:58:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the RootStatement object"""

from dataclasses import dataclass
from typing import List

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException
from SimpleSchema.Schema.Elements.Statements.Statement import Statement


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class RootStatement(Statement):
    """Collection of statements associated with a translation unit/file"""

    CHILDREN_NAME                           = "statements"

    # ----------------------------------------------------------------------
    statements: List[Statement]  # Can be an empty list

    # ----------------------------------------------------------------------
    def __post_init__(self):
        for statement in self.statements:
            if isinstance(statement, RootStatement):
                raise SimpleSchemaException(
                    "Root statements may not contain nested root statements.",
                    statement.range,
                )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptChildren(self) -> Element._GenerateAcceptChildrenGeneratorType:  # pragma: no coverage
        yield from self.statements