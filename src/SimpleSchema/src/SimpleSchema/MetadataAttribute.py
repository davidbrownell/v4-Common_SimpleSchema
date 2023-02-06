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

from dataclasses import dataclass
from enum import auto, IntFlag

from Common_Foundation.Types import extensionmethod

from .Schema.Elements.Common.Element import Element
from .Schema.Elements.Types.Type import Type

# TODO: Traits
#       - Inheritable
#       - Flag applied to resolved type

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
        TopLevelItem                        = auto()
        NestedItem                          = auto()

        TopLevelStructure                   = auto()
        NestedStructure                     = auto()

        TopLevelType                        = auto()
        NestedType                          = auto()

        _ElementTypeDelimiter               = auto()

        # Cardinality
        StandardCardinality                 = auto()
        OptionalCardinality                 = auto()
        CollectionCardinality               = auto()
        ZeroOrMoreCardinality               = auto()
        OneOrMoreCardinality                = auto()
        FixedCollectionCardinality          = auto()

        _CardinalityDelimiter               = auto()

        # Amalgamations
        Item                                = TopLevelItem | NestedItem
        Structure                           = TopLevelStructure | NestedStructure
        Type                                = TopLevelType | NestedType

        TopLevelElement                     = TopLevelItem | TopLevelStructure | TopLevelType
        NestedElement                       = NestedItem | NestedStructure | NestedType

        Element                             = Item | Structure | Type

        ElementMask                         = Element
        CardinalityMask                     = (_CardinalityDelimiter - 1) & ~ElementMask

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    flags: Flag

    name: str
    type: Type

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
