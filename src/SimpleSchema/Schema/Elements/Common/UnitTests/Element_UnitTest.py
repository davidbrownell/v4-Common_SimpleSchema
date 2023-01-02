# ----------------------------------------------------------------------
# |
# |  Element_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 09:24:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
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
from typing import Any, cast, Iterator, List, Optional, TextIO
from unittest import mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Types import overridemethod


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Element import Element, SimpleElement, Range, VisitResult


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MyElement(Element):
    # ----------------------------------------------------------------------
    name: SimpleElement
    number: SimpleElement
    children: List[SimpleElement]

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
        yield cast(List[Element], self.children)


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
    ):
        self._on_element_result             = on_element_result
        self._on_my_element_result          = on_my_element_result
        self._on_details_result             = on_details_result
        self._on_children_result            = on_children_result
        self._on_detail_item_result         = on_detail_item_result

        self.values: List[Any]              = []

    # ----------------------------------------------------------------------
    @contextmanager
    def OnElement(self, element) -> Iterator[Optional[VisitResult]]:
        self.values.append(element)
        yield self._on_element_result

    # ----------------------------------------------------------------------
    @contextmanager
    def OnElementDetails(self, element) -> Iterator[Optional[VisitResult]]:
        yield self._on_details_result

    # ----------------------------------------------------------------------
    @contextmanager
    def OnElementChildren(self, element) -> Iterator[Optional[VisitResult]]:
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
        value.Accept(self)
        return self._on_detail_item_result

    # ----------------------------------------------------------------------
    def OnMyElement__number(self, value, *, include_disabled) -> VisitResult:
        value.Accept(self)
        return VisitResult.Continue


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def test_SimpleElement():
    range_mock = mock.MagicMock()

    se = SimpleElement[str](range_mock, "the value")

    assert se.range is range_mock
    assert se.value == "the value"


# ----------------------------------------------------------------------
def test_Element():
    e = Element(Range.Create(Path("abcd"), 1, 2, 3, 4))
    assert e.range == Range.Create(Path("abcd"), 1, 2, 3, 4)


# ----------------------------------------------------------------------
def test_Disabled():
    e = Element(mock.MagicMock())

    assert e.is_disabled is False

    e.Disable()
    assert e.is_disabled is True


# ----------------------------------------------------------------------
def test_Parent():
    e = Element(mock.MagicMock())

    with pytest.raises(
        Exception,
        match=re.escape("A parent has not been set for this element."),
    ):
        e.parent

    parent = Element(mock.MagicMock())

    e.SetParent(parent)
    assert e.parent is parent

    e.SetParent(None)

    with pytest.raises(
        Exception,
        match=re.escape("A parent has not been set for this element."),
    ):
        e.parent


# ----------------------------------------------------------------------
class TestVisitor(object):
    # ----------------------------------------------------------------------
    def test_Standard(self, my_element):
        v = MyVisitor()

        my_element.Accept(v)

        assert v.values == [
            my_element,   # OnElement
            my_element,   # OnMyElement
            my_element.name,
            my_element.name.value,
            my_element.number,
            my_element.number.value,
            my_element.children[0],
            my_element.children[0].value,
            my_element.children[1],
            my_element.children[1].value,
        ]

    # ----------------------------------------------------------------------
    def test_OnElementTerminate(self, my_element):
        v = MyVisitor(
            on_element_result=VisitResult.Terminate,
        )

        assert my_element.Accept(v) == VisitResult.Terminate

        assert v.values == [
            my_element,
        ]

    # ----------------------------------------------------------------------
    def test_OnElementSkipAll(self, my_element):
        v = MyVisitor(
            on_element_result=VisitResult.SkipAll,
        )

        assert my_element.Accept(v) == VisitResult.Continue

        assert v.values == [
            my_element,
        ]

    # ----------------------------------------------------------------------
    def test_OnElementSkipDetails(self, my_element):
        v = MyVisitor(
            on_element_result=VisitResult.SkipDetails,
        )

        assert my_element.Accept(v) == VisitResult.Continue

        assert v.values == [
            my_element,
            my_element,
            my_element.children[0],
            my_element.children[0].value,
            my_element.children[1],
            my_element.children[1].value,
        ]

    # ----------------------------------------------------------------------
    def test_OnElementSkipChildren(self, my_element):
        v = MyVisitor(
            on_element_result=VisitResult.SkipChildren,
        )

        my_element.Accept(v)

        assert v.values == [
            my_element,   # OnElement
            my_element,   # OnMyElement
            my_element.name,
            my_element.name.value,
            my_element.number,
            my_element.number.value,
        ]

    # ----------------------------------------------------------------------
    def test_OnMyElementTerminate(self, my_element):
        v = MyVisitor(
            on_my_element_result=VisitResult.Terminate,
        )

        assert my_element.Accept(v) == VisitResult.Terminate

        assert v.values == [
            my_element,  # OnElement
            my_element,  # OnMyElement
        ]

    # ----------------------------------------------------------------------
    def test_OnMyElementSkipDetails(self, my_element):
        v = MyVisitor(
            on_my_element_result=VisitResult.SkipDetails,
        )

        assert my_element.Accept(v) == VisitResult.Continue

        assert v.values == [
            my_element,
            my_element,
            my_element.children[0],
            my_element.children[0].value,
            my_element.children[1],
            my_element.children[1].value,
        ]

    # ----------------------------------------------------------------------
    def test_OnMyElementSkipChildren(self, my_element):
        v = MyVisitor(
            on_my_element_result=VisitResult.SkipChildren,
        )

        assert my_element.Accept(v) == VisitResult.Continue

        assert v.values == [
            my_element,   # OnElement
            my_element,   # OnMyElement
            my_element.name,
            my_element.name.value,
            my_element.number,
            my_element.number.value,
        ]

    # ----------------------------------------------------------------------
    def test_OnDetailsTerminate(self, my_element):
        v = MyVisitor(
            on_details_result=VisitResult.Terminate,
        )

        assert my_element.Accept(v) == VisitResult.Terminate

        assert v.values == [
            my_element,
            my_element,
        ]

    # ----------------------------------------------------------------------
    def test_OnDetailsSkip(self, my_element):
        v = MyVisitor(
            on_details_result=VisitResult.SkipAll,
        )

        assert my_element.Accept(v) == VisitResult.Continue

        assert v.values == [
            my_element,
            my_element,
            my_element.children[0],
            my_element.children[0].value,
            my_element.children[1],
            my_element.children[1].value,
        ]

    # ----------------------------------------------------------------------
    def test_OnChildrenTerminate(self, my_element):
        v = MyVisitor(
            on_children_result=VisitResult.Terminate,
        )

        assert my_element.Accept(v) == VisitResult.Terminate

        assert v.values == [
            my_element,
            my_element,
            my_element.name,
            my_element.name.value,
            my_element.number,
            my_element.number.value,
        ]

    # ----------------------------------------------------------------------
    def test_OnChildrenSkip(self, my_element):
        v = MyVisitor(
            on_children_result=VisitResult.SkipChildren,
        )

        assert my_element.Accept(v) == VisitResult.Continue

        assert v.values == [
            my_element,
            my_element,
            my_element.name,
            my_element.name.value,
            my_element.number,
            my_element.number.value,
        ]

    # ----------------------------------------------------------------------
    def test_OnDetailItemTerminate(self, my_element):
        v = MyVisitor(
            on_detail_item_result=VisitResult.Terminate,
        )

        assert my_element.Accept(v) == VisitResult.Terminate

        assert v.values == [
            my_element,
            my_element,
            my_element.name,
            my_element.name.value,
        ]

    # ----------------------------------------------------------------------
    def test_Disabled(self, my_element):
        # Normal
        v = MyVisitor()

        assert my_element.Accept(v) == VisitResult.Continue

        assert v.values == [
            my_element,   # OnElement
            my_element,   # OnMyElement
            my_element.name,
            my_element.name.value,
            my_element.number,
            my_element.number.value,
            my_element.children[0],
            my_element.children[0].value,
            my_element.children[1],
            my_element.children[1].value,
        ]

        # Disabled
        my_element.Disable()

        v = MyVisitor()

        assert my_element.Accept(v) == VisitResult.Continue

        assert v.values == []

        # Disabled, but include
        v = MyVisitor()

        assert my_element.Accept(v, include_disabled=True) == VisitResult.Continue

        assert v.values == [
            my_element,   # OnElement
            my_element,   # OnMyElement
            my_element.name,
            my_element.name.value,
            my_element.number,
            my_element.number.value,
            my_element.children[0],
            my_element.children[0].value,
            my_element.children[1],
            my_element.children[1].value,
        ]


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
@pytest.fixture
def my_element() -> MyElement:
    return MyElement(
        Range.Create(Path("file1"), 1, 2, 3, 4),
        SimpleElement(Range.Create(Path("file2"), 10, 20, 30, 40), "the string"),
        SimpleElement(Range.Create(Path("file3"), 11, 21, 31, 41), 12345),
        [
            SimpleElement(Range.Create(Path("file4"), 100, 200, 300, 400), 2.35),
            SimpleElement(Range.Create(Path("file5"), 101, 201, 301, 401), -32),
        ],
    )
