# ----------------------------------------------------------------------
# |
# |  ContainerAttributes.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-06 15:07:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains MetadataAttributes that can be applied to containers"""

from dataclasses import dataclass
from typing import ClassVar

from .MetadataAttribute import MetadataAttribute

from ..Elements.Common.Cardinality import Cardinality

from ..Elements.Types.FundamentalTypes.StringType import StringType
from ..Elements.Types.ReferenceType import ReferenceType

from ...Common.Range import Range


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class PluralNameMetadataAttribute(MetadataAttribute):
    """Defines a plural name on an element"""

    # ----------------------------------------------------------------------
    flags: ClassVar[MetadataAttribute.Flag]             = MetadataAttribute.Flag.ContainerCardinality
    name: ClassVar[str]                                 = "plural_name"

    type: ClassVar[ReferenceType]                       = MetadataAttribute.CreateType(
        StringType(Range.CreateFromCode()),
        Cardinality.CreateFromCode(0, 1),
    )
