# ----------------------------------------------------------------------
# |
# |  RootStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 09:58:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the RootStatement object"""

from contextlib import contextmanager
from dataclasses import dataclass
from typing import cast, List

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
    @property
    def parent(self) -> None:
        return None

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
    def SetParent(
        self,
        element: Element,  # pylint: disable=unused-argument
    ) -> None:
        raise Exception("Root statements cannot have parents.")

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def _GenerateAcceptChildren(self) -> Element._GenerateAcceptChildrenGeneratorType:  # pragma: no coverage
        yield cast(List[Element], self.statements)
