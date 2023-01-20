# ----------------------------------------------------------------------
# |
# |  ExtensionStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 10:06:21
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ExtensionStatementKeywordArg and ExtensionStatement objects"""

from dataclasses import dataclass, field, InitVar
from typing import cast

from Common_Foundation.Types import overridemethod

from .Statement import Element, Statement

from ..Common.SimpleElement import SimpleElement
from ..Expressions.Expression import Expression

from ....Common import Errors


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ExtensionStatementKeywordArg(Element):
    """Keyword argument associated with an extension statement"""

    # ----------------------------------------------------------------------
    name: SimpleElement[str]
    expression: Expression

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "name", self.name
        yield "expression", self.expression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ExtensionStatement(Statement):
    """An extension/function statement"""

    # ----------------------------------------------------------------------
    name: SimpleElement[str]
    positional_args: list[Expression]

    keyword_args_param: InitVar[list[ExtensionStatementKeywordArg]]  # Can be an empty list
    keyword_args: dict[str, ExtensionStatementKeywordArg]                   = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        keyword_args_param: list[ExtensionStatementKeywordArg],
    ):
        keyword_args: dict[str, ExtensionStatementKeywordArg] = {}

        for keyword_arg in keyword_args_param:
            key = keyword_arg.name.value

            prev_value = keyword_args.get(key, None)
            if prev_value is not None:
                raise Errors.ExtensionStatementDuplicateKeywordArg.Create(
                    keyword_arg.name.range,
                    key,
                    prev_value.name.range,
                )

            keyword_args[key] = keyword_arg

        object.__setattr__(self, "keyword_args", keyword_args)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "name", self.name
        yield "positional_args", cast(list[Element], self.positional_args)
        yield "keyword_args", cast(list[Element], list(self.keyword_args.values()))
