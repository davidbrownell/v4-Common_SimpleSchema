# ----------------------------------------------------------------------
# |
# |  CompoundStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-14 11:35:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CompoundStatement object"""

from dataclasses import dataclass
from typing import List, Optional

from SimpleSchema.Schema.Impl.Common.Identifier import Identifier
from SimpleSchema.Schema.Impl.Expressions.MetadataExpression import MetadataExpression
from SimpleSchema.Schema.Impl.Statements.Statement import Statement
from SimpleSchema.Schema.Impl.Types.Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class CompoundStatement(Statement):
    """A Statement that contains other statements"""

    # ----------------------------------------------------------------------
    name: Identifier
    base: Optional[Type]
    metadata: Optional[MetadataExpression]
    statements: List[Statement]
