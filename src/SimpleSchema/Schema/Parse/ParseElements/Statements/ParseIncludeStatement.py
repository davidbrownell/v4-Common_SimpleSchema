# ----------------------------------------------------------------------
# |
# |  ParseIncludeStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-21 10:14:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseIncludeStatement and ParseIncludeStatementItem objects"""

from dataclasses import dataclass, field, InitVar
from enum import auto, Enum
from pathlib import Path
from typing import List, Optional

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element, SimpleElement
from SimpleSchema.Schema.Elements.Common.Identifier import Identifier, Visibility
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Statements.Statement import Statement


# ----------------------------------------------------------------------
class ParseIncludeStatementType(Enum):
    """Specifies the type of include statement encountered during parsing"""

    # from <directory> import <filename>
    Module                                  = auto()

    # from <filename> import <name_or_names>
    Named                                   = auto()

    # from <filename> import *
    Star                                    = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseIncludeStatementItem(Element):
    """Name explicitly included"""

    # ----------------------------------------------------------------------
    element_name: Identifier

    reference_name_param: InitVar[Optional[Identifier]]
    reference_name: Identifier              = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        reference_name_param: Optional[Identifier],
    ):
        if not self.element_name.is_type:
            raise SimpleSchemaException("Imported elements must be types.", self.element_name.range)

        if self.element_name.visibility.value != Visibility.Public:
            raise SimpleSchemaException(
                "'{}' is not a public type.".format(self.element_name.id.value),
                self.element_name.range,
            )

        if reference_name_param is None:
            reference_name_param = Identifier(
                self.element_name.id.range,
                self.element_name.id,
                SimpleElement(self.range, Visibility.Private),
            )

        if not reference_name_param.is_type:
            raise SimpleSchemaException("Reference elements must be types.", reference_name_param.range)

        object.__setattr__(self, "reference_name", reference_name_param)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "element_name", self.element_name

        if self.reference_name is not None:
            yield "reference_name", self.reference_name


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseIncludeStatement(Statement):
    """Includes content from another file"""

    # ----------------------------------------------------------------------
    include_type: ParseIncludeStatementType

    filename: SimpleElement[Path]
    items: List[ParseIncludeStatementItem]  # Can be empty

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.filename.value.is_file():
            raise SimpleSchemaException(
                "'{}' is not a valid file.".format(self.filename.value),
                self.filename.range,
            )

        if self.include_type in [
            ParseIncludeStatementType.Module,
            ParseIncludeStatementType.Star,
        ]:
            if self.items:
                raise SimpleSchemaException("No items were expected.", self.range)
        elif self.include_type == ParseIncludeStatementType.Named:
            if not self.items:
                raise SimpleSchemaException("Items were expected.", self.range)
        else:
            assert False, self.include_type  # pragma: no cover

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "filename", self.filename
        yield "items", self.items
