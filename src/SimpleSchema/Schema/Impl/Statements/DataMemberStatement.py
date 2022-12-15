# ----------------------------------------------------------------------
# |
# |  DataMemberStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 09:30:16
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MemberStatement object"""

from dataclasses import dataclass
from typing import Optional

from SimpleSchema.Schema.Impl.Expressions.IdentifierExpression import IdentifierExpression
from SimpleSchema.Schema.Impl.Expressions.MetadataExpression import MetadataExpression
from SimpleSchema.Schema.Impl.Statements.Statement import Statement
from SimpleSchema.Schema.Impl.Types.Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DataMemberStatement(Statement):
    """A data member of a type"""

    # ----------------------------------------------------------------------
    name: IdentifierExpression
    the_type: Type

    metadata: Optional[MetadataExpression]
