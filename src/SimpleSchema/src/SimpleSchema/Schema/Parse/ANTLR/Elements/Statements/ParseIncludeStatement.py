# ----------------------------------------------------------------------
# |
# |  ParseIncludeStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 09:00:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseIncludeStatement, ParseIncludeStatementItem, and ParseIncludeStatementType objects"""

from dataclasses import dataclass
from enum import auto, Enum
from pathlib import Path
from typing import cast

from Common_Foundation.Types import overridemethod

from ..Common.ParseIdentifier import ParseIdentifier

from .....Elements.Common.Element import Element
from .....Elements.Common.SimpleElement import SimpleElement

from .....Elements.Statements.Statement import Statement

from ......Common import Errors


# ----------------------------------------------------------------------
class ParseIncludeStatementType(Enum):
    """Specifies the type of include statement encountered during parsing"""

    # from <directory> import <filename_stem>
    Module                                  = auto()

    # from <filename> import <name_or_names>
    Named                                   = auto()

    # from <filename> import *
    Star                                    = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseIncludeStatementItem(Element):
    """Named item imported"""

    # ----------------------------------------------------------------------
    element_name: ParseIdentifier
    reference_name: ParseIdentifier

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.element_name.is_type:
            raise Errors.ParseIncludeStatementItemNotType.Create(
                self.element_name.range,
                self.element_name.value,
            )

        if not self.reference_name.is_type:
            raise Errors.ParseIncludeStatementItemReferenceNotPublic.Create(
                self.reference_name.visibility.range,
                self.reference_name.value,
            )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "element_name", self.element_name
        yield "reference_name", self.reference_name


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseIncludeStatement(Statement):
    """Statement that includes content from another file"""

    # ----------------------------------------------------------------------
    include_type: ParseIncludeStatementType

    filename: SimpleElement[Path]
    items: list[ParseIncludeStatementItem]  # Can be empty

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if not self.filename.value.is_file():
            raise Errors.ParseIncludeStatementInvalidFile.Create(self.filename.range, self.filename.value)

        if self.include_type in [
            ParseIncludeStatementType.Module,
            ParseIncludeStatementType.Star,
        ]:
            if self.items:
                raise Errors.ParseIncludeStatementInvalidItems.Create(self.range)
        elif self.include_type == ParseIncludeStatementType.Named:
            if not self.items:
                raise Errors.ParseIncludeStatementMissingItems.Create(self.range)
        else:
            assert False, self.include_type  # pragma: no cover

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "filename", self.filename
        yield "items", cast(list[Element], self.items)
