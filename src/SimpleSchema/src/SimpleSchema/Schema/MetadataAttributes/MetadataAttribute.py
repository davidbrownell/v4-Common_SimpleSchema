# ----------------------------------------------------------------------
# |
# |  MetadataAttribute.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-30 10:11:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MetadataAttribute object"""

from dataclasses import dataclass, field
from enum import auto, IntFlag

from Common_Foundation.Types import extensionmethod

from ..Elements.Common.Cardinality import Cardinality
from ..Elements.Common.Element import Element

from ..Elements.Types.BasicType import BasicType


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MetadataAttribute(object):
    """Defines an attribute that can be provided in SimpleSchema metadata"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class Flag(IntFlag):
        # Element Types
        RootItem                            = auto()
        NestedItem                          = auto()

        RootStructure                       = auto()
        NestedStructure                     = auto()

        RootType                            = auto()
        NestedType                          = auto()

        BaseType                            = auto()

        _ElementTypeDelimiter               = auto()

        # Cardinality
        SingleCardinality                   = auto()
        OptionalCardinality                 = auto()
        ContainerCardinality                = auto()
        ZeroOrMoreCardinality               = auto()
        OneOrMoreCardinality                = auto()
        FixedContainerCardinality           = auto()

        _CardinalityDelimiter               = auto()

        # Traits
        Inheritable                         = auto()

        _TraitsDelimiter                    = auto()

        # ----------------------------------------------------------------------
        # |  Amalgamations
        # ----------------------------------------------------------------------

        # Element Types
        Item                                = RootItem | NestedItem
        Structure                           = RootStructure | NestedStructure
        Type                                = RootType | NestedType

        RootElement                         = RootItem | RootStructure | RootType
        NestedElement                       = NestedItem | NestedStructure | NestedType

        Element                             = Item | Structure | Type

        # Masks
        ElementTypeMask                     = Element
        CardinalityMask                     = (_CardinalityDelimiter - 1) & (~ElementTypeMask | 0)
        TraitsMask                          = (_TraitsDelimiter -1) & (~ElementTypeMask | ~CardinalityMask)

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    flags: Flag

    name: str

    type: BasicType
    cardinality: Cardinality                = field(default_factory=lambda: Cardinality.CreateFromCode(0, 1))

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    @extensionmethod
    def Validate(
        self,
        element: Element,
    ) -> None:
        """Validate that an attribute applies and is valid for the provided element"""

        # No validation is performed by default
        pass
