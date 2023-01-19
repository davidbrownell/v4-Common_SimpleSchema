# ----------------------------------------------------------------------
# |
# |  ToPythonDictVisitor.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-16 11:39:42
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ToPythonDictVisitor object"""

from contextlib import contextmanager
from typing import Any, cast, Dict, Iterator, List, Optional, Union
from weakref import ReferenceType

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Element import Element, SimpleElement, SimpleElements, VisitResult
from SimpleSchema.Schema.Elements.Common.Identifier import Identifier
from SimpleSchema.Schema.Elements.Common.Metadata import Metadata, MetadataItem

from SimpleSchema.Schema.Elements.Expressions.BooleanExpression import BooleanExpression
from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
from SimpleSchema.Schema.Elements.Expressions.ListExpression import ListExpression
from SimpleSchema.Schema.Elements.Expressions.NumberExpression import NumberExpression
from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression
from SimpleSchema.Schema.Elements.Expressions.TupleExpression import TupleExpression

from SimpleSchema.Schema.Elements.Statements.ExtensionStatement import ExtensionStatement, ExtensionStatementKeywordArg
from SimpleSchema.Schema.Elements.Statements.ItemStatement import ItemStatement
from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement
from SimpleSchema.Schema.Elements.Statements.StructureStatement import StructureStatement

from SimpleSchema.Schema.Elements.Types.FundamentalTypes import BooleanType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes import DateType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes import DateTimeType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes import DirectoryType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes import DurationType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes import EnumType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes import FilenameType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes import GuidType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes import IntegerType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes import NumberType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes import StringType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes import TimeType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes import UriType

from SimpleSchema.Schema.Elements.Types.AliasType import AliasType
from SimpleSchema.Schema.Elements.Types.StructureType import StructureType
from SimpleSchema.Schema.Elements.Types.TupleType import TupleType
from SimpleSchema.Schema.Elements.Types.VariantType import VariantType

from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseIncludeStatement import ParseIncludeStatement, ParseIncludeStatementItem
from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseItemStatement import ParseItemStatement
from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseStructureStatement import ParseStructureStatement

from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseIdentifierType import ParseIdentifierType
from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseTupleType import ParseTupleType
from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseVariantType import ParseVariantType

from SimpleSchema.Schema.Visitors.Visitor import Visitor


# ----------------------------------------------------------------------
#pylint: disable=unused-argument


# ----------------------------------------------------------------------
class ToPythonDictVisitor(Visitor):
    """Converts items to a python dict"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        *,
        add_disabled_status: bool=False,
    ):
        self.add_disabled_status            = add_disabled_status

        self._stack: List[Dict[str, Any]]               = []
        self._processing_reference_element_ctr          = 0

    # ----------------------------------------------------------------------
    @property
    def root(self) -> List[Dict[str, Any]]:
        assert len(self._stack) == 1, self._stack
        return self._stack

    # ----------------------------------------------------------------------
    def __getattr__(
        self,
        name: str,
    ):
        match = self.DETAILS_REGEX.match(name)
        if match:
            return lambda *args, **kwargs: self._DefaultDetailMethod(match.group("member_name"), *args, **kwargs)

        # match = self.METHOD_REGEX.match(name)
        # if match:
        #     return self._DefaultMethod

        raise AttributeError(name)

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnElement(
        self,
        element: Element,
    ) -> Iterator[Optional[VisitResult]]:
        self._stack.append(
            {
                "__type__": element.__class__.__name__,
                "range": element.range.ToString(),
            },
        )

        if self.add_disabled_status:
            self._stack[-1]["disabled"] = element.is_disabled

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnElementChildren(
        self,
        element: Element,
    ) -> Iterator[Optional[VisitResult]]:
        prev_num_items = len(self._stack)

        yield

        children = self._stack[prev_num_items:]
        self._stack = self._stack[:prev_num_items]

        d = self._stack[-1]

        d[element.CHILDREN_NAME] = children

    # ----------------------------------------------------------------------
    @contextmanager
    def OnSimpleElement(
        self,
        element: SimpleElement,
    ) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        value = element.value

        if value is not None and not isinstance(value, (str, int, float, bool)):
            value = str(value)

        d["value"] = value

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnSimpleElements(
        self,
        element: SimpleElements,
    ) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    # |  Common
    # ----------------------------------------------------------------------
    @contextmanager
    def OnCardinality(self, element: Cardinality) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnIdentifier(self, element: Identifier) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnMetadata(self, element: Metadata) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnMetadataItem(self, element: MetadataItem) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    # |  Expressions
    # ----------------------------------------------------------------------
    @contextmanager
    def OnBooleanExpression(self, element: BooleanExpression) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        d.update(
            value=element.value,
        )

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnIntegerExpression(self, element: IntegerExpression) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        d.update(
            value=element.value,
        )

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnListExpression(self, element: ListExpression) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        d.update(
            items=element.items,
        )

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnNumberExpression(self, element: NumberExpression) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        d.update(
            value=element.value,
        )

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnStringExpression(self, element: StringExpression) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        d.update(
            value=element.value,
        )

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTupleExpression(self, element: TupleExpression) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        d.update(
            expressions=element.expressions,
        )

        yield

    # ----------------------------------------------------------------------
    # |  Statements
    # ----------------------------------------------------------------------
    @contextmanager
    def OnExtensionStatement(self, element: ExtensionStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnExtensionStatementKeywordArg(self, element: ExtensionStatementKeywordArg) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnItemStatement(self, element: ItemStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnRootStatement(self, element: RootStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnParseIncludeStatement(self, element: ParseIncludeStatement) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        d.update(
            include_type=str(element.include_type),
        )

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnParseIncludeStatementItem(self, element: ParseIncludeStatementItem) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnParseItemStatement(self, element: ParseItemStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnParseStructureStatement(self, element: ParseStructureStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    # |  Types
    # ----------------------------------------------------------------------
    @contextmanager
    def OnBooleanType(self, element: BooleanType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnDateType(self, element: DateType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnDateTimeType(self, element: DateTimeType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnDirectoryType(self, element: DirectoryType) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        d.update(
            ensure_exists=element.ensure_exists,
        )

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnDurationType(self, element: DurationType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnEnumType(self, element: EnumType) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        d.update(
            values=element.values,
            starting_value=element.starting_value,
        )

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnFilenameType(self, element: FilenameType) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        d.update(
            ensure_exists=element.ensure_exists,
            match_any=element.match_any,
        )

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnGuidType(self, element: GuidType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnIntegerType(self, element: IntegerType) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        if element.min is not None:
            d["min"] = element.min
        if element.max is not None:
            d["max"] = element.max
        if element.bits is not None:
            d["bits"] = str(element.bits)

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnNumberType(self, element: NumberType) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        if element.min is not None:
            d["min"] = element.min
        if element.max is not None:
            d["max"] = element.max
        if element.bits is not None:
            d["bits"] = str(element.bits)

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnStringType(self, element: StringType) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        d["min_length"] = element.min_length

        if element.max_length is not None:
            d["max_length"] = element.max_length
        if element.validation_expression is not None:
            d["validation_expression"] = element.validation_expression

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTimeType(self, element: TimeType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnUriType(self, element: UriType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnAliasType(self, element: AliasType) -> Iterator[Optional[VisitResult]]:
        if self._processing_reference_element_ctr:
            d = self._stack[-1]

            d["alias"] = {
                "name": element.name.id.value,
                "range": element.type.range.ToString(),
            }

            yield VisitResult.SkipAll
            return

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnStructureType(self, element: StructureType) -> Iterator[Optional[VisitResult]]:
        if self._processing_reference_element_ctr != 0:
            d = self._stack[-1]

            d["struct"] = {
                "name": element.statement.name.id.value,
                "range": element.statement.range.ToString(),
            }

            yield VisitResult.SkipAll
            return

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTupleType(self, element: TupleType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnVariantType(self, element: VariantType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnParseIdentifierType(self, element: ParseIdentifierType) -> Iterator[Optional[VisitResult]]:
        if element.is_global_reference:
            self._stack[-1]["is_global_reference"] = element.is_global_reference.ToString()

        if element.is_element_reference:
            self._stack[-1]["is_element_reference"] = element.is_element_reference.ToString()

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnParseTupleType(self, element: ParseTupleType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnParseVariantType(self, element: ParseVariantType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @contextmanager
    def _DefaultMethod(
        self,
        element: Element,
    ) -> Iterator[Optional[VisitResult]]:
        yield None

    # ----------------------------------------------------------------------
    def _DefaultDetailMethod(
        self,
        member_name: str,
        element_or_elements: Element.GenerateAcceptDetailsGeneratorItemsType,
        *,
        include_disabled: bool,
    ) -> None:
        prev_num_elements = len(self._stack)

        elements: Optional[
            Union[
                List[Element],
                List[ReferenceType[Element]],
            ],
        ] = None

        if isinstance(element_or_elements, list):
            is_list = True
            elements = cast(List[Element], element_or_elements)
        else:
            is_list = False
            elements = [element_or_elements, ]  # type: ignore

        assert elements is not None

        for element in elements:
            if isinstance(element, Element):
                element.Accept(self, include_disabled=include_disabled)
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
                    element.Accept(self, include_disabled=include_disabled)

        children = self._stack[prev_num_elements:]
        self._stack = self._stack[:prev_num_elements]

        if not is_list:
            assert 0 <= len(children) <= 1
            if children:
                children = children[0]
            else:
                children = None

        d = self._stack[-1]

        d[member_name] = children
