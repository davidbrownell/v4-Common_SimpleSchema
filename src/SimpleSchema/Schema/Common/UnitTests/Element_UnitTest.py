# ----------------------------------------------------------------------
# |
# |  Element_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 09:00:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Element.py"""

import re
import sys

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast, Iterator, Optional
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Types import overridemethod


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Common.Element import Element, VisitResult
    from SimpleSchema.Schema.Common.SimpleElement import SimpleElement


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MyElement(Element):
    # ----------------------------------------------------------------------
    name: SimpleElement[str]
    number: SimpleElement[float]
    children: list[SimpleElement[int]]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:
        yield "name", self.name
        yield "number", self.number

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def _GenerateAcceptChildren(self) -> Element._GenerateAcceptChildrenGeneratorType:
        yield cast(list[Element], self.children)


# ----------------------------------------------------------------------
class MyVisitor(object):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        *,
        on_element_result: Optional[VisitResult]=None,
        on_my_element_result: Optional[VisitResult]=None,
        on_details_result: Optional[VisitResult]=None,
        on_children_result: Optional[VisitResult]=None,
        on_detail_item_result: Optional[VisitResult]=None,
        on_child_item_result: Optional[VisitResult]=None,
    ):
        self._on_element_result             = on_element_result
        self._on_my_element_result          = on_my_element_result
        self._on_details_result             = on_details_result
        self._on_children_result            = on_children_result
        self._on_detail_item_result         = on_detail_item_result
        self._on_child_item_result          = on_child_item_result

        self.values: list[Any]              = []
        self._in_children_ctr: int          = 0

    # ----------------------------------------------------------------------
    @contextmanager
    def OnElement(self, element) -> Iterator[Optional[VisitResult]]:
        self.values.append(element)
        yield self._on_child_item_result if self._in_children_ctr else self._on_element_result

    # ----------------------------------------------------------------------
    @contextmanager
    def OnElementDetails(self, element) -> Iterator[Optional[VisitResult]]:
        yield self._on_details_result

    # ----------------------------------------------------------------------
    @contextmanager
    def OnElementChildren(self, element) -> Iterator[Optional[VisitResult]]:
        self._in_children_ctr += 1

        # ----------------------------------------------------------------------
        def OnExit():
            self._in_children_ctr -= 1

        # ----------------------------------------------------------------------

        with ExitStack(OnExit):
            yield self._on_children_result

    # ----------------------------------------------------------------------
    @contextmanager
    def OnSimpleElement(self, element) -> Iterator[VisitResult]:
        self.values.append(element.value)
        yield VisitResult.Continue

    # ----------------------------------------------------------------------
    @contextmanager
    def OnMyElement(self, element) -> Iterator[Optional[VisitResult]]:
        self.values.append(element)
        yield self._on_my_element_result

    # ----------------------------------------------------------------------
    def OnMyElement__name(self, value, *, include_disabled) -> Optional[VisitResult]:
        value.Accept(self, include_disabled=include_disabled)
        return self._on_detail_item_result

    # ----------------------------------------------------------------------
    def OnMyElement__number(self, value, *, include_disabled) -> VisitResult:
        value.Accept(self, include_disabled=include_disabled)
        return VisitResult.Continue


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def test_Element():
    range_mock = Mock()
    name = SimpleElement[str](Mock(), "First Last")
    number = SimpleElement[float](Mock(), 1.23)

    children = [
        SimpleElement[int](Mock(), 10),
        SimpleElement[int](Mock(), 20),
        SimpleElement[int](Mock(), 30),
    ]

    e = MyElement(range_mock, name, number, children)

    assert e.range is range_mock
    assert e.name is name
    assert e.number is number
    assert e.children is children


# ----------------------------------------------------------------------
def test_Parent(_element):
    with pytest.raises(
        Exception,
        match=re.escape("A parent has not been set for this element."),
    ):
        _element.parent

    _element.SetParent(_element)
    assert _element.parent is _element

    with pytest.raises(
        Exception,
        match=re.escape("A parent has already been set for this element."),
    ):
        _element.SetParent(_element)


# ----------------------------------------------------------------------
def test_Disable(_element):
    assert _element.is_disabled is False

    _element.Disable()
    assert _element.is_disabled is True

    with pytest.raises(
        Exception,
        match=re.escape("The element is already disabled."),
    ):
        _element.Disable()


# ----------------------------------------------------------------------
class TestVisitor(object):
    # ----------------------------------------------------------------------
    def test_Standard(self, _element):
        v = MyVisitor()

        assert _element.Accept(v) == VisitResult.Continue

        assert v.values == [
            _element,   # OnElement
            _element,   # OnMyElement
            _element.name,
            _element.name.value,
            _element.number,
            _element.number.value,
            _element.children[0],
            _element.children[0].value,
            _element.children[1],
            _element.children[1].value,
            _element.children[2],
            _element.children[2].value,
            _element.children[3],
            _element.children[3].value,
        ]

    # ----------------------------------------------------------------------
    def test_OnElementTerminate(self, _element):
        v = MyVisitor(
            on_element_result=VisitResult.Terminate,
        )

        assert _element.Accept(v) == VisitResult.Terminate

        assert v.values == [
            _element,
        ]

    # ----------------------------------------------------------------------
    def test_OnElementSkipAll(self, _element):
        v = MyVisitor(
            on_element_result=VisitResult.SkipAll,
        )

        assert _element.Accept(v) == VisitResult.Continue

        assert v.values == [
            _element,
        ]

    # ----------------------------------------------------------------------
    def test_OnElementSkipDetails(self, _element):
        v = MyVisitor(
            on_element_result=VisitResult.SkipDetails,
        )

        assert _element.Accept(v) == VisitResult.Continue

        assert v.values == [
            _element,   # OnElement
            _element,   # OnMyElement
            _element.children[0],
            _element.children[0].value,
            _element.children[1],
            _element.children[1].value,
            _element.children[2],
            _element.children[2].value,
            _element.children[3],
            _element.children[3].value,
        ]

    # ----------------------------------------------------------------------
    def test_OnElementSkipChildren(self, _element):
        v = MyVisitor(
            on_element_result=VisitResult.SkipChildren,
        )

        assert _element.Accept(v) == VisitResult.Continue

        assert v.values == [
            _element,   # OnElement
            _element,   # OnMyElement
            _element.name,
            _element.name.value,
            _element.number,
            _element.number.value,
        ]

    # ----------------------------------------------------------------------
    def test_OnMyElementTerminate(self, _element):
        v = MyVisitor(
            on_my_element_result=VisitResult.Terminate,
        )

        assert _element.Accept(v) == VisitResult.Terminate

        assert v.values == [
            _element,   # OnElement
            _element,   # OnMyElement,
        ]

    # ----------------------------------------------------------------------
    def test_OnMyElementSkipAll(self, _element):
        v = MyVisitor(
            on_my_element_result=VisitResult.SkipAll,
        )

        assert _element.Accept(v) == VisitResult.Continue

        assert v.values == [
            _element,   # OnElement
            _element,   # OnMyElement,
        ]

    # ----------------------------------------------------------------------
    def test_OnMyElementSkipDetails(self, _element):
        v = MyVisitor(
            on_my_element_result=VisitResult.SkipDetails,
        )

        assert _element.Accept(v) == VisitResult.Continue

        assert v.values == [
            _element,   # OnElement
            _element,   # OnMyElement
            _element.children[0],
            _element.children[0].value,
            _element.children[1],
            _element.children[1].value,
            _element.children[2],
            _element.children[2].value,
            _element.children[3],
            _element.children[3].value,
        ]

    # ----------------------------------------------------------------------
    def test_OnMyElementSkipChildren(self, _element):
        v = MyVisitor(
            on_my_element_result=VisitResult.SkipChildren,
        )

        assert _element.Accept(v) == VisitResult.Continue

        assert v.values == [
            _element,   # OnElement
            _element,   # OnMyElement
            _element.name,
            _element.name.value,
            _element.number,
            _element.number.value,
        ]

    # ----------------------------------------------------------------------
    def test_OnDetailsTerminate(self, _element):
        v = MyVisitor(
            on_details_result=VisitResult.Terminate,
        )

        assert _element.Accept(v) == VisitResult.Terminate

        assert v.values == [
            _element,   # OnElement
            _element,   # OnMyElement
        ]

    # ----------------------------------------------------------------------
    def test_OnDetailsSkip(self, _element):
        v = MyVisitor(
            on_details_result=VisitResult.SkipDetails,
        )

        assert _element.Accept(v) == VisitResult.Continue

        assert v.values == [
            _element,   # OnElement
            _element,   # OnMyElement
            _element.children[0],
            _element.children[0].value,
            _element.children[1],
            _element.children[1].value,
            _element.children[2],
            _element.children[2].value,
            _element.children[3],
            _element.children[3].value,
        ]

    # ----------------------------------------------------------------------
    def test_OnChildrenTerminate(self, _element):
        v = MyVisitor(
            on_children_result=VisitResult.Terminate,
        )

        assert _element.Accept(v) == VisitResult.Terminate

        assert v.values == [
            _element,   # OnElement
            _element,   # OnMyElement
            _element.name,
            _element.name.value,
            _element.number,
            _element.number.value,
        ]

    # ----------------------------------------------------------------------
    def test_OnChildrenSkip(self, _element):
        v = MyVisitor(
            on_children_result=VisitResult.SkipChildren,
        )

        assert _element.Accept(v) == VisitResult.Continue

        assert v.values == [
            _element,   # OnElement
            _element,   # OnMyElement
            _element.name,
            _element.name.value,
            _element.number,
            _element.number.value,
        ]

    # ----------------------------------------------------------------------
    def test_OnDetailItemTerminate(self, _element):
        v = MyVisitor(
            on_detail_item_result=VisitResult.Terminate,
        )

        assert _element.Accept(v) == VisitResult.Terminate

        assert v.values == [
            _element,   # OnElement
            _element,   # OnMyElement
            _element.name,
            _element.name.value,
        ]

    # ----------------------------------------------------------------------
    def test_OnChildItemTerminate(self, _element):
        v = MyVisitor(
            on_child_item_result=VisitResult.Terminate,
        )

        assert _element.Accept(v) == VisitResult.Terminate

        assert v.values == [
            _element,   # OnElement
            _element,   # OnMyElement
            _element.name,
            _element.name.value,
            _element.number,
            _element.number.value,
            _element.children[0],
        ]

    # ----------------------------------------------------------------------
    def test_Disabled(self, _element):
        # Standard
        v = MyVisitor()

        _element.number.Disable()
        _element.children[0].Disable()
        _element.children[3].Disable()

        assert _element.Accept(v) == VisitResult.Continue

        assert v.values == [
            _element,   # OnElement
            _element,   # OnMyElement
            _element.name,
            _element.name.value,
            _element.children[1],
            _element.children[1].value,
            _element.children[2],
            _element.children[2].value,
        ]

        # Include Disabled
        v = MyVisitor()

        assert _element.Accept(v, include_disabled=True) == VisitResult.Continue

        assert v.values == [
            _element,   # OnElement
            _element,   # OnMyElement
            _element.name,
            _element.name.value,
            _element.number,
            _element.number.value,
            _element.children[0],
            _element.children[0].value,
            _element.children[1],
            _element.children[1].value,
            _element.children[2],
            _element.children[2].value,
            _element.children[3],
            _element.children[3].value,
        ]


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
@pytest.fixture
def _element() -> MyElement:
    return MyElement(
        Mock(),
        SimpleElement[str](Mock(), "First Last"),
        SimpleElement[float](Mock(), 1.23),
        [
            SimpleElement[int](Mock(), 1),
            SimpleElement[int](Mock(), 2),
            SimpleElement[int](Mock(), 3),
            SimpleElement[int](Mock(), 4),
        ],
    )
