# ----------------------------------------------------------------------
# |
# |  RootStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 14:09:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the RootStatement object"""

from dataclasses import dataclass
from contextlib import contextmanager
from typing import cast, ClassVar

from Common_Foundation.Types import overridemethod

from .Statement import Element, Statement
from ....Common import Errors


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class RootStatement(Statement):
    """Collection of statements associated with a translation unit/file"""

    # ----------------------------------------------------------------------
    CHILDREN_NAME: ClassVar[str]            = "statements"

    statements: list[Statement]  # Can be an empty list

    # ----------------------------------------------------------------------
    def __post_init__(self):
        for statement in self.statements:
            if isinstance(statement, RootStatement):
                raise Errors.RootStatementInvalidNested.Create(statement.range)

    # ----------------------------------------------------------------------
    @property
    def parent(self) -> None:
        return None

    # ----------------------------------------------------------------------
    def SetParent(
        self,
        element: Element,  # pylint: disable=unused-argument
    ) -> None:
        raise ValueError("Root statements cannot have parents.")

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def _GenerateAcceptChildren(self) -> Element._GenerateAcceptChildrenGeneratorType:  # pragma: no coverage
        yield cast(list[Element], self.statements)
