# ----------------------------------------------------------------------
# |
# |  Metadata.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-16 09:17:54
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Metadata and MetadataItem objects"""

from dataclasses import dataclass, field, InitVar
from typing import Dict, List

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Impl.Common.Element import Element
from SimpleSchema.Schema.Impl.Common.SimpleSchemaException import SimpleSchemaException
from SimpleSchema.Schema.Impl.Expressions.IdentifierExpression import IdentifierExpression, Expression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MetadataItem(Element):
    """Individual metadata item within a collection of metadata items"""

    # ----------------------------------------------------------------------
    name: IdentifierExpression
    value: Expression

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "name", self.name
        yield "value", self.value


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Metadata(Element):
    """Collection of metadata items"""

    CHILDREN_NAME                           = "items"

    # ----------------------------------------------------------------------
    items_param: InitVar[List[MetadataItem]]
    items: Dict[str, MetadataItem]          = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        items_param: List[MetadataItem],
    ) -> None:
        items: Dict[str, MetadataItem] = {}

        for item in items_param:
            key = item.name.id.value

            prev_value = items.get(key, None)
            if prev_value is not None:
                raise SimpleSchemaException(
                    "The metadata item '{}' has already been provided at {}.".format(
                        key,
                        prev_value.name.range.ToString(include_filename=False),
                    ),
                    item.name.range,
                )

            items[key] = item

        object.__setattr__(self, "items", items)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptChildren(self) -> Element._GenerateAcceptChildrenGeneratorType:  # pragma: no cover
        yield from self.items.values()
