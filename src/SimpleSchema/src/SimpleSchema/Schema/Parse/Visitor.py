# ----------------------------------------------------------------------
# |
# |  Visitor.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 13:36:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Visitor object"""

from contextlib import contextmanager
from typing import Iterator, Optional

from Common_Foundation.Types import extensionmethod

from .ANTLR.Elements.Common.ParseIdentifier import ParseIdentifier

from .ANTLR.Elements.Statements.ParseIncludeStatement import ParseIncludeStatement, ParseIncludeStatementItem
from .ANTLR.Elements.Statements.ParseItemStatement import ParseItemStatement
from .ANTLR.Elements.Statements.ParseStructureStatement import ParseStructureStatement

from .ANTLR.Elements.Types.ParseIdentifierType import ParseIdentifierType
from .ANTLR.Elements.Types.ParseTupleType import ParseTupleType
from .ANTLR.Elements.Types.ParseVariantType import ParseVariantType

from ..Visitors.Visitor import Visitor as VisitorBase, VisitResult


# ----------------------------------------------------------------------
# pylint: disable=unused-argument


# ----------------------------------------------------------------------
class Visitor(VisitorBase):
    # ----------------------------------------------------------------------
    # |
    # |  Common
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnParseIdentifier(self, element: ParseIdentifier) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    # |
    # |  Statements
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnParseIncludeStatement(self, element: ParseIncludeStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnParseIncludeStatementItem(self, element: ParseIncludeStatementItem) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnParseItemStatement(self, element: ParseItemStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnParseStructureStatement(self, element: ParseStructureStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    # |
    # |  Types
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnParseIdentifierType(self, element: ParseIdentifierType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnParseTupleType(self, element: ParseTupleType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnParseVariantType(self, element: ParseVariantType) -> Iterator[Optional[VisitResult]]:
        yield
