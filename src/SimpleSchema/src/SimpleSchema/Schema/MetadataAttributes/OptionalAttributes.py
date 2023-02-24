# ----------------------------------------------------------------------
# |
# |  OptionalAttributes.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-03 10:21:51
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains MetadataAttributes that can be applied to optional Elements"""

from dataclasses import dataclass, field
from typing import ClassVar, Optional

from .MetadataAttribute import MetadataAttribute

from ..Elements.Common.Cardinality import Cardinality
from ..Elements.Common.SimpleElement import SimpleElement
from ..Elements.Common.Visibility import Visibility

from ..Elements.Types.BasicType import BasicType
from ..Elements.Types.FundamentalTypes.BooleanType import BooleanType
from ..Elements.Types.FundamentalTypes.IntegerType import IntegerType
from ..Elements.Types.FundamentalTypes.NumberType import NumberType
from ..Elements.Types.FundamentalTypes.StringType import StringType
from ..Elements.Types.ReferenceType import ReferenceType
from ..Elements.Types.VariantType import VariantType

from ...Common.Range import Range


# ----------------------------------------------------------------------
def _CreateType(
    basic_type: BasicType,
    cardinality: Optional[Cardinality]=None,
) -> ReferenceType:
    return ReferenceType.Create(
        Range.CreateFromCode(),
        SimpleElement[Visibility](Range.CreateFromCode(), Visibility.Private),
        SimpleElement[str](Range.CreateFromCode(), basic_type.NAME),
        basic_type,
        cardinality or Cardinality.CreateFromCode(),
        None,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DefaultMetadataAttribute(MetadataAttribute):
    """Defines a default value for an optional item"""

    # ----------------------------------------------------------------------
    flags: ClassVar[MetadataAttribute.Flag]             = (
        MetadataAttribute.Flag.OptionalCardinality
        | MetadataAttribute.Flag.Inheritable
    )

    name: ClassVar[str]                                 = "default"

    type: BasicType                                     = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        variant = VariantType(
            Range.CreateFromCode(),
            [
                _CreateType(BooleanType(Range.CreateFromCode())),
                _CreateType(IntegerType(Range.CreateFromCode())),
                _CreateType(NumberType(Range.CreateFromCode())),
                _CreateType(StringType(Range.CreateFromCode())),
            ],
        )

        variant = VariantType(
            Range.CreateFromCode(),
            [
                _CreateType(variant),
                _CreateType(variant, Cardinality.CreateFromCode(1, None)),
            ],
        )

        object.__setattr__(self, "type", variant)
