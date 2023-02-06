# ----------------------------------------------------------------------
# |
# |  TupleType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 10:38:26
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleType object"""

import itertools

from dataclasses import dataclass
from functools import cached_property
from typing import Any, cast, ClassVar, Optional, Tuple, Type as PythonType, Union

from Common_Foundation.Types import DoesNotExist, overridemethod

from Common_FoundationEx.InflectEx import inflect

from .Type import Type

from ..Common.Cardinality import Cardinality
from ..Common.Element import Element
from ..Common.Metadata import Metadata

from ..Expressions.TupleExpression import Expression, TupleExpression

from ....Common import Errors
from ....Common.Range import Range
from ....Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TupleType(Type):
    """A list of types"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "Tuple"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = (tuple, )

    types: list[Type]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.types:
            raise Errors.TupleTypeNoTypes.Create(self.range)

        super(TupleType, self).__post_init__()

    # ----------------------------------------------------------------------
    @overridemethod
    def ItemToPython(
        self,
        expression_or_value: Union[Expression, Any],
    ) -> Any:
        if isinstance(expression_or_value, Expression):
            if not isinstance(expression_or_value, TupleExpression):
                raise Errors.TupleTypeTupleExpressionExpected.Create(expression_or_value.range)

            tuple_items: list[Any] = []

            for sub_type, sub_expression in itertools.zip_longest(
                self.types,
                expression_or_value.value,
                fillvalue=DoesNotExist.instance,
            ):
                if isinstance(sub_type, DoesNotExist) or isinstance(sub_expression, DoesNotExist):
                    raise SimpleSchemaException(
                        expression_or_value.range,
                        Errors.tuple_type_item_mismatch.format(
                            value=inflect.no("tuple item", len(self.types)),
                            value_verb=inflect.plural_verb("was", len(self.types)),
                            found=inflect.no("tuple item", len(expression_or_value.value)),
                            found_verb=inflect.plural_verb("was", len(expression_or_value.value)),
                        ),
                    )

                try:
                    tuple_items.append(sub_type.ToPython(sub_expression))
                except SimpleSchemaException as ex:
                    ex.ranges.append(expression_or_value.range)
                    raise

            return tuple(tuple_items)

        return super(TupleType, self).ItemToPython(expression_or_value)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @cached_property
    @overridemethod
    def _display_name(self) -> str:
        return "({}, )".format(", ".join(sub_type.display_name for sub_type in self.types))

    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield from super(TupleType, self)._GenerateAcceptDetails()

        yield "types", cast(list[Element], self.types)

    # ----------------------------------------------------------------------
    @overridemethod
    def _ItemToPythonImpl(
        self,
        value: Tuple[Any, ...],
    ) -> Tuple[Any, ...]:
        tuple_items: list[Any] = []

        for sub_type, sub_value in itertools.zip_longest(self.types, value, fillvalue=DoesNotExist.instance):
            if isinstance(sub_type, DoesNotExist) or isinstance(sub_value, DoesNotExist):
                raise Exception(
                    Errors.tuple_type_item_mismatch.format(
                        value=inflect.no("tuple item", len(self.types)),
                        value_verb=inflect.plural_verb("was", len(self.types)),
                        found=inflect.no("tuple item", len(value)),
                        found_verb=inflect.plural_verb("was", len(value)),
                    ),
                )

            tuple_items.append(sub_type.ToPython(sub_value))

        return tuple(tuple_items)
