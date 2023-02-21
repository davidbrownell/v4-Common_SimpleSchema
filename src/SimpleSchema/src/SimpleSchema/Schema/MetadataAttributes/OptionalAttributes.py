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

from dataclasses import dataclass
from typing import ClassVar

from .MetadataAttribute import MetadataAttribute

from ..Elements.Common.Cardinality import Cardinality

from ..Elements.Types.FundamentalTypes.BooleanType import BooleanType
from ..Elements.Types.FundamentalTypes.IntegerType import IntegerType
from ..Elements.Types.FundamentalTypes.NumberType import NumberType
from ..Elements.Types.FundamentalTypes.StringType import StringType
from ..Elements.Types.ReferenceType import ReferenceType
from ..Elements.Types.VariantType import VariantType

from ...Common.Range import Range


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

    type: ClassVar[ReferenceType]                       = MetadataAttribute.CreateType(
        VariantType(
            Range.CreateFromCode(),
            [
                MetadataAttribute.CreateType(BooleanType(Range.CreateFromCode())),
                MetadataAttribute.CreateType(IntegerType(Range.CreateFromCode())),
                MetadataAttribute.CreateType(NumberType(Range.CreateFromCode())),
                MetadataAttribute.CreateType(StringType(Range.CreateFromCode())),
                # ListType
                # TupleType
            ],
        ),
        Cardinality.CreateFromCode(0, 1),
    )
