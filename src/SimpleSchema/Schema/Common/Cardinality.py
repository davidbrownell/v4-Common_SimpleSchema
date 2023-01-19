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
from typing import Optional

from Common_Foundation.Types import overridemethod

from .Element import Element
from .Metadata import Metadata

from ..Elements.Expressions.IntegerExpression import IntegerExpression

from ...Common import Errors
from ...Common.Range import Range


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
            raise Errors.InvalidCardinalityRange.Create(max_param.range, min_param.value, max_param.value)

        # Commit the results
        object.__setattr__(self, "min", min_param)
        object.__setattr__(self, "max", max_param)

        if self.is_single and self.metadata is not None:
            raise Errors.InvalidCardinalityMetadata.Create(self.metadata.range)

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
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "min", self.min

        if self.max is not None:
            yield "max", self.max

        if self.metadata is not None:
            yield "metadata", self.metadata
