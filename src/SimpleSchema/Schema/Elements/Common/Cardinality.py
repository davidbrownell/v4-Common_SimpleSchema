# ----------------------------------------------------------------------
# |
# |  Cardinality.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-16 09:01:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Cardinality object"""

from dataclasses import dataclass, field, InitVar
from typing import Optional

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.Metadata import Metadata
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException
from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression


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
                # Nothing to do here, this indicates an unbounded number of items
                pass
            else:
                assert False, (min_param, max_param)  # pragma: no cover

        assert min_param is not None

        if max_param is not None and max_param.value < min_param.value:
            raise SimpleSchemaException(
                "Invalid cardinality ({} > {}).".format(
                    min_param.value,
                    max_param.value,
                ),
                max_param.range,
            )

        # Commit the values
        object.__setattr__(self, "min", min_param)
        object.__setattr__(self, "max", max_param)

        if self.is_single and self.metadata is not None:
            raise SimpleSchemaException(
                "Metadata cannot be associated with single elements.",
                self.metadata.range,
            )

    # ----------------------------------------------------------------------
    @property
    def is_single(self) -> bool:
        return self.min.value == 1 and self.max is not None and self.max.value == 1

    @property
    def is_optional(self) -> bool:
        return self.min.value == 0 and self.max is not None and self.max.value == 1

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no coverage
        yield "min", self.min

        if self.max is not None:
            yield "max", self.max

        if self.metadata is not None:
            yield "metadata", self.metadata
