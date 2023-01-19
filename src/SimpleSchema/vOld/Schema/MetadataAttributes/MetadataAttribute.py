# ----------------------------------------------------------------------
# |
# |  MetadataAttribute.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-01 08:54:01
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

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Types.Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MetadataAttribute(object):
    """Defines an attribute that can be provided in metadata"""

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

        _ElementTypeDelimiter               = auto()

        # Cardinality
        StandardCardinality                 = auto()
        OptionalCardinality                 = auto()
        CollectionCardinality               = auto()
        ZeroOrMoreCardinality               = auto()
        OneOrMoreCardinality                = auto()

        _CardinalityDelimiter               = auto()

        # Amalgamations
        Item                                = TopLevelItem | NestedItem
        Structure                           = TopLevelStructure | NestedStructure
        Element                             = Item | Structure

        TopLevelElement                     = TopLevelItem | TopLevelStructure
        NestedElement                       = NestedItem | NestedStructure

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
        element: Element,  # pylint: disable=unused-argument
    ) -> None:
        """Validates that the attribute is valid for the given element"""

        # No validation is performed by default
        return
