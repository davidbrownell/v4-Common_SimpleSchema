# ----------------------------------------------------------------------
# |
# |  VariantType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-04 14:24:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantType object"""

from dataclasses import dataclass
from functools import cached_property
from typing import Any, cast, List, Optional

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Element import Element, SimpleElements
from SimpleSchema.Schema.Elements.Common.Metadata import Metadata
from SimpleSchema.Schema.Elements.Common.Range import Range
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Expressions.Expression import Expression

from SimpleSchema.Schema.Elements.Types.Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class VariantType(Type):
    """One of the types"""

    # ----------------------------------------------------------------------
    NAME = "Variant"

    # ----------------------------------------------------------------------
    types: List[Type]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.types:
            raise SimpleSchemaException("No types were provided.", self.range)

        for contained_type in self.types:
            if isinstance(contained_type, VariantType):
                raise SimpleSchemaException("Nested variant types are not supported.", contained_type.range)

    # ----------------------------------------------------------------------
    @cached_property
    @overridemethod
    def display_name(self) -> str:
        return "({})".format(" | ".join(the_type.display_name for the_type in self.types))

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "types", cast(List[Element], self.types)

        yield from super(VariantType, self)._GenerateAcceptDetails()

    # ----------------------------------------------------------------------
    @overridemethod
    def _CreateAcceptReferenceDetails(self) -> Element:
        return SimpleElements(
            self.range,
            [
                child_type._CreateAcceptReferenceDetails()  # pylint: disable=protected-access
                for child_type in self.types
            ],
        )

    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(
        self,
        range_value: Range,
        cardinality: Cardinality,
        metadata: Optional[Metadata],
    ) -> Type:
        return VariantType(range_value, cardinality, metadata, self.types)

    # ----------------------------------------------------------------------
    @overridemethod
    def _ParseExpressionImpl(
        self,
        expression: Expression,
    ) -> Any:
        for the_type in self.types:
            try:
                return the_type.ParseExpression(expression)
            except SimpleSchemaException:
                pass

        raise SimpleSchemaException("The expression is not valid for any of the variant types.", expression.range)
