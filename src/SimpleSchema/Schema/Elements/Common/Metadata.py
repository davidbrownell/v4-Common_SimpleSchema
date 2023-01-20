# ----------------------------------------------------------------------
# |
# |  Metadata.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 09:46:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Metadata and MetadataItem objects"""

from contextlib import contextmanager
from dataclasses import dataclass, field, InitVar
from typing import cast, ClassVar

from Common_Foundation.Types import overridemethod

from .Element import Element
from .SimpleElement import SimpleElement

from ..Expressions.Expression import Expression

from ....Common import Errors


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MetadataItem(Element):
    """Individual metadata within a collection of metadata items"""

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
class Metadata(Element):
    """Collection of metadata items"""

    # ----------------------------------------------------------------------
    CHILDREN_NAME: ClassVar[str]            = "items"

    items_param: InitVar[list[MetadataItem]]    # Can be an empty list
    items: dict[str, MetadataItem]          = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        items_param: list[MetadataItem],
    ) -> None:
        items: dict[str, MetadataItem] = {}

        for item in items_param:
            key = item.name.value

            prev_value = items.get(key, None)
            if prev_value is not None:
                raise Errors.MetadataItemDuplicated.Create(item.name.range, key, prev_value.name.range)

            items[key] = item

        object.__setattr__(self, "items", items)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def _GenerateAcceptChildren(self) -> Element._GenerateAcceptChildrenGeneratorType:  # pragma: no cover
        yield cast(list[Element], list(self.items.values()))
