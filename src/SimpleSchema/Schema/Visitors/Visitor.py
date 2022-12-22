# ----------------------------------------------------------------------
# |
# |  Visitor.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-16 10:52:02
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Visitor object"""

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Iterator, Optional

from Common_Foundation.Types import extensionmethod

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Element import Element, VisitResult
from SimpleSchema.Schema.Elements.Common.Identifier import Identifier
from SimpleSchema.Schema.Elements.Common.Metadata import Metadata, MetadataItem

from SimpleSchema.Schema.Elements.Expressions.BooleanExpression import BooleanExpression
from SimpleSchema.Schema.Elements.Expressions.IdentifierExpression import IdentifierExpression
from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
from SimpleSchema.Schema.Elements.Expressions.ListExpression import ListExpression
from SimpleSchema.Schema.Elements.Expressions.NumberExpression import NumberExpression
from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression

from SimpleSchema.Schema.Elements.Statements.ExtensionStatement import ExtensionStatement, ExtensionStatementKeywordArg
from SimpleSchema.Schema.Elements.Statements.IncludeStatement import IncludeStatement, IncludeStatementItem
from SimpleSchema.Schema.Elements.Statements.ItemStatement import ItemStatement
from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement
from SimpleSchema.Schema.Elements.Statements.StructureStatement import StructureStatement

from SimpleSchema.Schema.Elements.Types.IdentifierType import IdentifierType
from SimpleSchema.Schema.Elements.Types.TupleType import TupleType
from SimpleSchema.Schema.Elements.Types.VariantType import VariantType

# Convenience imports
from SimpleSchema.Schema.Elements.Common.Element import SimpleElement           # pylint: disable=unused-import
from SimpleSchema.Schema.Elements.Common.Identifier import Visibility           # pylint: disable=unused-import
from SimpleSchema.Schema.Elements.Common.Location import Location               # pylint: disable=unused-import
from SimpleSchema.Schema.Elements.Common.Range import Range                     # pylint: disable=unused-import


# ----------------------------------------------------------------------
class Visitor(ABC):
    """Visitor base class"""

    # ----------------------------------------------------------------------
    # |  Generic Methods
    # ----------------------------------------------------------------------
    @extensionmethod
    @contextmanager
    def OnElement(
        self,
        element: Element,  # pylint: disable=unused-argument
    ) -> Iterator[Optional[VisitResult]]:
        yield VisitResult.Continue

    # ----------------------------------------------------------------------
    @extensionmethod
    @contextmanager
    def OnElementDetails(
        self,
        element: Element,  # pylint: disable=unused-argument
    ) -> Iterator[Optional[VisitResult]]:
        yield VisitResult.Continue

    # ----------------------------------------------------------------------
    @extensionmethod
    @contextmanager
    def OnElementChildren(
        self,
        element: Element,  # pylint: disable=unused-argument
    ) -> Iterator[Optional[VisitResult]]:
        yield VisitResult.Continue

    # ----------------------------------------------------------------------
    # |  Common Methods
    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnCardinality(self, element: Cardinality) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnIdentifier(self, element: Identifier) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnMetadata(self, element: Metadata) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnMetadataItem(self, element: MetadataItem) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |  Expressions
    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnBooleanExpression(self, element: BooleanExpression) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnIdentifierExpression(self, element: IdentifierExpression) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnIntegerExpression(self, element: IntegerExpression) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnListExpression(self, element: ListExpression) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnNumberExpression(self, element: NumberExpression) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnStringExpression(self, element: StringExpression) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |  Statements
    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnIncludeStatement(self, element: IncludeStatement) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnIncludeStatementItem(self, element: IncludeStatementItem) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnExtensionStatement(self, element: ExtensionStatement) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnExtensionStatementKeywordArg(self, element: ExtensionStatementKeywordArg) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnItemStatement(self, element: ItemStatement) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnRootStatement(self, element: RootStatement) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |  Types
    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnIdentifierType(self, element: IdentifierType) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnTupleType(self, element: TupleType) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    @contextmanager
    def OnVariantType(self, element: VariantType) -> Iterator[Optional[VisitResult]]:
        raise Exception("Abstract method")  # pragma: no cover
