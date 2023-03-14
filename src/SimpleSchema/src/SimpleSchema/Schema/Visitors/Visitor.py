# ----------------------------------------------------------------------
# |
# |  Visitor.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 13:28:44
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

import re

from abc import ABC
from contextlib import contextmanager
from typing import Iterator, Optional, Union
from weakref import ReferenceType as WeakReferenceType

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation.Types import extensionmethod

from ..Elements.Common.Cardinality import Cardinality
from ..Elements.Common.Element import Element, VisitResult
from ..Elements.Common.Metadata import Metadata, MetadataItem
from ..Elements.Common.SimpleElement import SimpleElement

from ..Elements.Expressions.BooleanExpression import BooleanExpression
from ..Elements.Expressions.IntegerExpression import IntegerExpression
from ..Elements.Expressions.ListExpression import ListExpression
from ..Elements.Expressions.NoneExpression import NoneExpression
from ..Elements.Expressions.NumberExpression import NumberExpression
from ..Elements.Expressions.StringExpression import StringExpression
from ..Elements.Expressions.TupleExpression import TupleExpression

from ..Elements.Statements.ExtensionStatement import ExtensionStatement, ExtensionStatementKeywordArg
from ..Elements.Statements.ItemStatement import ItemStatement
from ..Elements.Statements.RootStatement import RootStatement
from ..Elements.Statements.StructureStatement import StructureStatement

from ..Elements.Types.FundamentalTypes.BooleanType import BooleanType
from ..Elements.Types.FundamentalTypes.DateTimeType import DateTimeType
from ..Elements.Types.FundamentalTypes.DateType import DateType
from ..Elements.Types.FundamentalTypes.DirectoryType import DirectoryType
from ..Elements.Types.FundamentalTypes.DurationType import DurationType
from ..Elements.Types.FundamentalTypes.EnumType import EnumType
from ..Elements.Types.FundamentalTypes.FilenameType import FilenameType
from ..Elements.Types.FundamentalTypes.GuidType import GuidType
from ..Elements.Types.FundamentalTypes.IntegerType import IntegerType
from ..Elements.Types.FundamentalTypes.NumberType import NumberType
from ..Elements.Types.FundamentalTypes.StringType import StringType
from ..Elements.Types.FundamentalTypes.TimeType import TimeType
from ..Elements.Types.FundamentalTypes.UriType import UriType

from ..Elements.Types.ReferenceType import ReferenceType
from ..Elements.Types.StructureType import StructureType
from ..Elements.Types.TupleType import TupleType
from ..Elements.Types.VariantType import VariantType

# ----------------------------------------------------------------------
# pylint: disable=unused-argument


# ----------------------------------------------------------------------
class Visitor(ABC):
    """Base class for Element visitors"""

    METHOD_REGEX                            = re.compile("^On(?P<object_name>.+)$")
    DETAILS_REGEX                           = re.compile("^On(?P<object_name>.+?)__(?P<member_name>.+)$")

    # ----------------------------------------------------------------------
    def __init__(self):
        self._processing_reference_element_ctr          = 0

        self.element_stack: list[Element]               = []

    # ----------------------------------------------------------------------
    @property
    def is_processing_reference_element(self) -> bool:
        return self._processing_reference_element_ctr != 0

    # ----------------------------------------------------------------------
    def __getattr__(
        self,
        name: str,
    ):
        match = self.DETAILS_REGEX.match(name)
        if match:
            return lambda *args, **kwargs: self._DefaultDetailMethod(match.group("member_name"), *args, **kwargs)

        raise AttributeError(name)

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnElement(self, element: Element) -> Iterator[Optional[VisitResult]]:
        self.element_stack.append(element)
        with ExitStack(self.element_stack.pop):
            yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnElementDetails(self, element: Element) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnElementChildren(self, element: Element) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnElementDetailsItem(self, name: str, element_or_elements: Element.GenerateAcceptDetailsGeneratorItemsType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    # |
    # |  Common
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnCardinality(self, element: Cardinality) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnMetadata(self, element: Metadata) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnMetadataItem(self, element: MetadataItem) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnSimpleElement(self, element: SimpleElement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    # |
    # |  Expressions
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnBooleanExpression(self, element: BooleanExpression) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnIntegerExpression(self, element: IntegerExpression) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnListExpression(self, element: ListExpression) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnNoneExpression(self, element: NoneExpression) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnNumberExpression(self, element: NumberExpression) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnStringExpression(self, element: StringExpression) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnTupleExpression(self, element: TupleExpression) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    # |
    # |  Statements
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnExtensionStatement(self, element: ExtensionStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnExtensionStatementKeywordArg(self, element: ExtensionStatementKeywordArg) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnItemStatement(self, element: ItemStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnRootStatement(self, element: RootStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    # |
    # |  Types
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnBooleanType(self, element: BooleanType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnDateTimeType(self, element: DateTimeType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnDateType(self, element: DateType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnDirectoryType(self, element: DirectoryType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnDurationType(self, element: DurationType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnFilenameType(self, element: FilenameType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnEnumType(self, element: EnumType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnGuidType(self, element: GuidType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnIntegerType(self, element: IntegerType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnNumberType(self, element: NumberType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnReferenceType(self, element: ReferenceType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnStringType(self, element: StringType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnStructureType(self, element: StructureType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnTimeType(self, element: TimeType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnTupleType(self, element: TupleType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnUriType(self, element: UriType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnVariantType(self, element: VariantType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _DefaultDetailMethod(
        self,
        member_name: str,
        element_or_elements: Element.GenerateAcceptDetailsGeneratorItemsType,
        *,
        include_disabled: bool,
    ) -> Optional[VisitResult]:
        with self.OnElementDetailsItem(member_name, element_or_elements) as visit_result:
            if visit_result == VisitResult.Terminate:
                return visit_result

            if visit_result and (visit_result & VisitResult.SkipAll):
                return VisitResult.Continue

            elements: Optional[
                Union[
                    list[Element],
                    list[WeakReferenceType[Element]],
                ],
            ] = None

            if isinstance(element_or_elements, list):
                elements = element_or_elements
            else:
                elements = [element_or_elements, ]  # type: ignore

            assert elements is not None

            for element in elements:
                if isinstance(element, Element):
                    visit_result = element.Accept(self, include_disabled=include_disabled)
                    if visit_result == VisitResult.Terminate:
                        return visit_result

                else:
                    element = element()
                    assert element is not None

                    self._processing_reference_element_ctr += 1

                    # ----------------------------------------------------------------------
                    def OnExit():
                        assert self._processing_reference_element_ctr != 0
                        self._processing_reference_element_ctr -= 1

                    # ----------------------------------------------------------------------

                    with ExitStack(OnExit):
                        visit_result = element.Accept(self, include_disabled=include_disabled)
                        if visit_result == VisitResult.Terminate:
                            return visit_result

        return VisitResult.Continue
