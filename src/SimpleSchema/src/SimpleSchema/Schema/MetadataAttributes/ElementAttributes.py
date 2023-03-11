# ----------------------------------------------------------------------
# |
# |  ElementAttributes.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-03 10:08:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains MetadataAttributes that can be applied to Elements"""

from dataclasses import dataclass, field
from typing import Any, ClassVar, Optional

from Common_Foundation.Types import overridemethod

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
@dataclass(frozen=True)
class NameMetadataAttribute(MetadataAttribute):
    """Define a name on an Element"""

    # ----------------------------------------------------------------------
    flags: ClassVar[MetadataAttribute.Flag]             = MetadataAttribute.Flag.NoRestrictions
    name: ClassVar[str]                                 = "name"
    type: ClassVar[BasicType]                           = StringType(Range.CreateFromCode())


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DescriptionMetadataAttribute(MetadataAttribute):
    """Apply a description to an Element"""

    # ----------------------------------------------------------------------
    flags: ClassVar[MetadataAttribute.Flag]             = MetadataAttribute.Flag.NoRestrictions
    name: ClassVar[str]                                 = "description"
    type: ClassVar[BasicType]                           = StringType(Range.CreateFromCode())


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DefaultMetadataAttribute(MetadataAttribute):
    """Defines a default value if the Element is not present"""

    # ----------------------------------------------------------------------
    flags: ClassVar[MetadataAttribute.Flag]             = MetadataAttribute.Flag.Inheritable
    name: ClassVar[str]                                 = "default"
    type: BasicType                                     = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        # ----------------------------------------------------------------------
        def CreateType(
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

        variant = VariantType(
            Range.CreateFromCode(),
            [
                CreateType(BooleanType(Range.CreateFromCode())),
                CreateType(IntegerType(Range.CreateFromCode())),
                CreateType(NumberType(Range.CreateFromCode())),
                CreateType(StringType(Range.CreateFromCode())),
            ],
        )

        variant = VariantType(
            Range.CreateFromCode(),
            [
                CreateType(variant),
                CreateType(variant, Cardinality.CreateFromCode(1, None)),
            ],
        )

        # TODO: Add support for N dimensional arrays

        object.__setattr__(self, "type", variant)

    # ----------------------------------------------------------------------
    @overridemethod
    def PostprocessValue(
        self,
        reference_type: ReferenceType,
        value: Any,
    ) -> Any:
        return reference_type.ToPython(value)
