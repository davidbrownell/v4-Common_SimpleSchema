# ----------------------------------------------------------------------
# |
# |  MetadataExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-13 09:54:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MetadataExpression and MetadataExpressionItem objects"""

from dataclasses import dataclass, field, InitVar
from typing import Dict, List

from SimpleSchema.Schema.Impl.Common.Element import Element
from SimpleSchema.Schema.Impl.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Impl.Expressions.Expression import Expression
from SimpleSchema.Schema.Impl.Expressions.IdentifierExpression import IdentifierExpression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MetadataExpressionItem(Element):
    """Individual metadata item within a collection of metadata items"""

    # ----------------------------------------------------------------------
    name: IdentifierExpression
    value: Element


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MetadataExpression(Expression):
    """Collection of names and values"""

    # ----------------------------------------------------------------------
    items_param: InitVar[List[MetadataExpressionItem]]
    items: Dict[str, MetadataExpressionItem]            = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        items_param: List[MetadataExpressionItem],
    ) -> None:
        items: Dict[str, MetadataExpressionItem] = {}

        for item in items_param:
            key = item.name.value

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
