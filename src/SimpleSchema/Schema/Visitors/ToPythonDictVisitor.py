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
from typing import Any, Dict, Iterator, List, Optional, Union

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element, SimpleElement, VisitResult

from SimpleSchema.Schema.Elements.Expressions.BooleanExpression import BooleanExpression
from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
from SimpleSchema.Schema.Elements.Expressions.NumberExpression import NumberExpression
from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression

from SimpleSchema.Schema.Parse.ParseElements.Statements.ParseIncludeStatement import ParseIncludeStatement, ParseIncludeStatementType
from SimpleSchema.Schema.Parse.ParseElements.Types.ParseIdentifierType import ParseIdentifierType

from SimpleSchema.Schema.Visitors.Visitor import Visitor


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

        self._stack: List[Dict[str, Any]]   = []

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

        match = self.METHOD_REGEX.match(name)
        if match:
            return self._DefaultMethod

        raise AttributeError(name)

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnElement(
        self,
        element: Element,  # pylint: disable=unused-argument
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
        element: Element,  # pylint: disable=unused-argument
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
    # |  Statements
    # ----------------------------------------------------------------------
    @contextmanager
    def OnParseIncludeStatement(self, element: ParseIncludeStatement) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        d.update(
            include_type=str(element.include_type),
        )

        yield

    # ----------------------------------------------------------------------
    # |  Types
    # ----------------------------------------------------------------------
    @contextmanager
    def OnParseIdentifierType(self, element: ParseIdentifierType) -> Iterator[Optional[VisitResult]]:
        if element.is_global_reference:
            self._stack[-1]["is_global_reference"] = element.is_global_reference.ToString()

        if element.is_element_reference:
            self._stack[-1]["is_element_reference"] = element.is_element_reference.ToString()

        yield

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @contextmanager
    def _DefaultMethod(
        self,
        element: Element,  # pylint: disable=unused-argument
    ) -> Iterator[Optional[VisitResult]]:
        yield None

    # ----------------------------------------------------------------------
    def _DefaultDetailMethod(
        self,
        member_name: str,
        element_or_elements: Union[Element, List[Element]],
        *,
        include_disabled: bool,
    ) -> None:
        prev_num_elements = len(self._stack)

        if isinstance(element_or_elements, list):
            is_list = True

            for element in element_or_elements:
                if not element.is_disabled or include_disabled:
                    element.Accept(
                        self,
                        include_disabled=include_disabled,
                    )
        else:
            is_list = False

            if not element_or_elements.is_disabled or include_disabled:
                element_or_elements.Accept(
                    self,
                    include_disabled=include_disabled,
                )

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
