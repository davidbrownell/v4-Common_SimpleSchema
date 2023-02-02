# ----------------------------------------------------------------------
# |
# |  Cardinality.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 09:43:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Cardinality object"""

from dataclasses import dataclass, field, InitVar
from functools import cached_property
from typing import Any, Optional, Union

from Common_Foundation.Types import overridemethod
from Common_FoundationEx.InflectEx import inflect

from .Element import Element
from .Metadata import Metadata

from ..Expressions.Expression import Expression
from ..Expressions.IntegerExpression import IntegerExpression

from ....Common import Errors
from ....Common.Range import Range
from ....Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Cardinality(Element):
    """Specifies the minimum and maximum number of items expected within a collection"""

    # ----------------------------------------------------------------------
    min_param: InitVar[Optional[IntegerExpression]]
    max_param: InitVar[Optional[IntegerExpression]]

    min: IntegerExpression                  = field(init=False)
    max: Optional[IntegerExpression]        = field(init=False)

    metadata: Optional[Metadata]

    # ----------------------------------------------------------------------
    @classmethod
    def CreateFromCode(
        cls,
        min_value: Optional[int]=None,
        max_value: Optional[int]=None,
        *,
        range_value: Optional[Range]=None,
        metadata: Optional[Metadata]=None,
    ) -> "Cardinality":
        if min_value is None:
            min_param = None
        else:
            min_param = IntegerExpression(Range.CreateFromCode(), min_value)

        if max_value is None:
            max_param = None
        else:
            max_param = IntegerExpression(Range.CreateFromCode(), max_value)

        if range_value is None:
            range_value = Range.CreateFromCode(callstack_offset=1)

        return cls(range_value, min_param, max_param, metadata)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        min_param: Optional[IntegerExpression],
        max_param: Optional[IntegerExpression],
    ) -> None:
        if min_param is None or max_param is None:
            if min_param is None and max_param is None:
                min_param = IntegerExpression(self.range, 1)
                max_param = IntegerExpression(self.range, 1)

            elif min_param is None:
                min_param = IntegerExpression(self.range, 0)

            elif max_param is None:
                # Nothing to do here as this indicates an unbounded number of items
                pass

            else:
                assert False, (min_param, max_param)  # pragma: no cover

        assert min_param is not None

        if max_param is not None and max_param.value < min_param.value:
            raise Errors.CardinalityInvalidRange.Create(max_param.range, min_param.value, max_param.value)

        # Commit the results
        object.__setattr__(self, "min", min_param)
        object.__setattr__(self, "max", max_param)

        if self.is_single and self.metadata is not None:
            raise Errors.CardinalityInvalidMetadata.Create(self.metadata.range)

    # ----------------------------------------------------------------------
    def __str__(self) -> str:
        return self._string

    # ----------------------------------------------------------------------
    @cached_property
    def is_single(self) -> bool:
        return self.min.value == 1 and self.max is not None and self.max.value == 1

    @cached_property
    def is_optional(self) -> bool:
        return self.min.value == 0 and self.max is not None and self.max.value == 1

    @cached_property
    def is_container(self) -> bool:
        return self.max is None or self.max.value > 1

    # ----------------------------------------------------------------------
    def Validate(
        self,
        expression_or_value: Union[Expression, Any],
    ) -> None:
        # ----------------------------------------------------------------------
        def Impl(
            value: Any,
        ) -> None:
            if self.is_container:
                if not isinstance(value, list):
                    raise Exception(Errors.cardinality_validate_list_required)

                num_items = len(value)

                if num_items < self.min.value:
                    raise Exception(
                        Errors.cardinality_validate_list_too_small.format(
                            value=inflect.no("item", self.min.value),
                            value_verb=inflect.plural_verb("was", self.min.value),
                            found=inflect.no("item", num_items),
                            found_verb=inflect.plural_verb("was", num_items),
                        ),
                    )

                if self.max is not None and num_items > self.max.value:
                    raise Exception(
                        Errors.cardinality_validate_list_too_large.format(
                            value=inflect.no("item", self.max.value),
                            value_verb=inflect.plural_verb("was", self.max.value),
                            found=inflect.no("item", num_items),
                            found_verb=inflect.plural_verb("was", num_items),
                        ),
                    )

                return

            if isinstance(value, list):
                raise Exception(Errors.cardinality_validate_list_not_expected)

            if value is None and not self.is_optional:
                raise Exception(Errors.cardinality_validate_none_not_expected)

            return

        # ----------------------------------------------------------------------

        if isinstance(expression_or_value, Expression):
            try:
                Impl(expression_or_value.value)
                return
            except Exception as ex:
                raise SimpleSchemaException(expression_or_value.range, str(ex)) from ex

        Impl(expression_or_value)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @cached_property
    def _string(self) -> str:
        if self.is_single:
            return ""

        if self.is_optional:
            return "?"

        assert self.is_container

        if self.max is None:
            if self.min.value == 0:
                return "*"

            if self.min.value == 1:
                return "+"

            return "[{}+]".format(self.min.value)

        assert self.max is not None

        if self.min.value == self.max.value:
            return "[{}]".format(self.min.value)

        return "[{}, {}]".format(self.min.value, self.max.value)

    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "min", self.min

        if self.max is not None:
            yield "max", self.max

        if self.metadata is not None:
            yield "metadata", self.metadata
