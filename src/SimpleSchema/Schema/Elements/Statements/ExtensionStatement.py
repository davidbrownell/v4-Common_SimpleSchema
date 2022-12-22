# ----------------------------------------------------------------------
# |
# |  ExtensionStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-14 09:39:49
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ExtensionStatement, ExtensionStatementPositionalArg, and ExtensionStatementKeywordArg objects"""

from dataclasses import dataclass, field, InitVar
from typing import Dict, List

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Expressions.IdentifierExpression import Identifier
from SimpleSchema.Schema.Elements.Statements.Statement import Statement


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ExtensionStatementKeywordArg(Element):
    """Keyword argument"""

    # ----------------------------------------------------------------------
    name: Identifier
    value: Element

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "name", self.name
        yield "value", self.value


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ExtensionStatement(Statement):
    """A extension/function invocation"""

    # ----------------------------------------------------------------------
    name: Identifier
    positional_args: List[Element]  # Can be an empty list

    keyword_args_param: InitVar[List[ExtensionStatementKeywordArg]]  # Can be an empty list
    keyword_args: Dict[str, ExtensionStatementKeywordArg]                   = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        keyword_args_param: List[ExtensionStatementKeywordArg],
    ) -> None:
        keyword_args: Dict[str, ExtensionStatementKeywordArg] = {}

        for keyword_arg in keyword_args_param:
            key = keyword_arg.name.id.value

            prev_value = keyword_args.get(key, None)
            if prev_value is not None:
                raise SimpleSchemaException(
                    "An argument for the parameter '{}' has already been provided at {}.".format(
                        key,
                        prev_value.name.range.ToString(include_filename=False),
                    ),
                    keyword_arg.name.range,
                )

            keyword_args[key] = keyword_arg

        object.__setattr__(self, "keyword_args", keyword_args)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "name", self.name
        yield "positional_args", self.positional_args
        yield "keyword_args", list(self.keyword_args.values())
