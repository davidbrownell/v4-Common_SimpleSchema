# ----------------------------------------------------------------------
# |
# |  Cardinality_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 10:27:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Cardinality.py"""

import re
import sys

from pathlib import Path
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Common.Range import Range
    from SimpleSchema.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
    from SimpleSchema.Schema.Elements.Common.Metadata import Metadata

    from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression


# ----------------------------------------------------------------------
def test_CreateFromCode():
    c = Cardinality.CreateFromCode()

    assert c.range.filename == Path(__file__)
    assert c.range.begin.line == c.range.end.line == 44

    assert c.is_single

    c = Cardinality.CreateFromCode(1, 2)

    assert c.range.filename == Path(__file__)
    assert c.range.begin.line == c.range.end.line == 51

    assert c.is_container

    assert c.min.value == 1
    assert c.min.range.filename.name == "Cardinality.py"

    assert c.max is not None
    assert c.max.value == 2
    assert c.max.range.filename.name == "Cardinality.py"

    assert c.min.range.begin.line < c.max.range.begin.line


# ----------------------------------------------------------------------
def test_Single():
    range_mock = Mock()

    c = Cardinality(range_mock, None, None)

    assert c.range is range_mock

    assert c.min.value == 1
    assert c.min.range is range_mock

    assert c.max is not None
    assert c.max.value == 1
    assert c.max.range is range_mock

    assert c.is_single
    assert c.is_optional is False
    assert c.is_container is False


# ----------------------------------------------------------------------
def test_Optional():
    range_mock = Mock()
    expression_mock = Mock()

    c = Cardinality(range_mock, None, IntegerExpression(expression_mock, 1))

    assert c.range is range_mock

    assert c.min.value == 0
    assert c.min.range is range_mock

    assert c.max is not None
    assert c.max.value == 1
    assert c.max.range is expression_mock

    assert c.is_single is False
    assert c.is_optional
    assert c.is_container is False


# ----------------------------------------------------------------------
def test_ContainerBounded():
    range_mock = Mock()
    min_expression_mock = Mock()
    max_expression_mock = Mock()

    c = Cardinality(
        range_mock,
        IntegerExpression(min_expression_mock, 0),
        IntegerExpression(max_expression_mock, 3),
    )

    assert c.range is range_mock

    assert c.min.value == 0
    assert c.min.range is min_expression_mock

    assert c.max is not None
    assert c.max.value == 3
    assert c.max.range is max_expression_mock

    assert c.is_single is False
    assert c.is_optional is False
    assert c.is_container


# ----------------------------------------------------------------------
def test_ContainerUnbounded():
    range_mock = Mock()
    min_expression_mock = Mock()

    c = Cardinality(
        range_mock,
        IntegerExpression(min_expression_mock, 0),
        None,
    )

    assert c.range is range_mock

    assert c.min.value == 0
    assert c.min.range is min_expression_mock

    assert c.max is None

    assert c.is_single is False
    assert c.is_optional is False
    assert c.is_container


# ----------------------------------------------------------------------
def test_Strings():
    assert str(Cardinality.CreateFromCode()) == ""
    assert str(Cardinality.CreateFromCode(0, 1)) == "?"
    assert str(Cardinality.CreateFromCode(0)) == "*"
    assert str(Cardinality.CreateFromCode(1)) == "+"
    assert str(Cardinality.CreateFromCode(3)) == "[3+]"
    assert str(Cardinality.CreateFromCode(3, 3)) == "[3]"
    assert str(Cardinality.CreateFromCode(3, 10)) == "[3, 10]"


# ----------------------------------------------------------------------
def test_ErrorInvalidCardinality():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Invalid cardinality (10 > 1). (file <Ln 1, Col 3 -> Ln 5, Col 7>)"),
    ):
        Cardinality(
            Mock(),
            IntegerExpression(Mock(), 10),
            IntegerExpression(Range.Create(Path("file"), 1, 3, 5, 7), 1),
        )


# ----------------------------------------------------------------------
class TestValidate(object):
    # ----------------------------------------------------------------------
    def test_Single(self):
        c = Cardinality(Mock(), None, None)

        c.Validate(10)
        c.Validate(IntegerExpression(Mock(), 10))

    # ----------------------------------------------------------------------
    def test_Optional(self):
        c = Cardinality.CreateFromCode(0, 1)

        c.Validate(10)
        c.Validate(IntegerExpression(Mock(), 10))
        c.Validate(None)

    # ----------------------------------------------------------------------
    def test_Container(self):
        c = Cardinality.CreateFromCode(2, 2)

        c.Validate([10, 20])
        c.Validate([IntegerExpression(Mock(), 10), IntegerExpression(Mock(), 20)])

    # ----------------------------------------------------------------------
    def test_ErrorContainerWithoutListPython(self):
        with pytest.raises(
            Exception,
            match=re.escape("A list of items was expected."),
        ):
            Cardinality.CreateFromCode(2, 2).Validate(10)

    # ----------------------------------------------------------------------
    def test_ErrorContainerWithoutListExpression(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("A list of items was expected. (filename <Ln 1, Col 2 -> Ln 3, Col 4>)"),
        ):
            Cardinality.CreateFromCode(2, 2).Validate(
                IntegerExpression(Range.Create(Path("filename"), 1, 2, 3, 4), 10),
            )

    # ----------------------------------------------------------------------
    def test_ErrorNotContainerWithList(self):
        with pytest.raises(
            Exception,
            match=re.escape("A list of items was not expected."),
        ):
            Cardinality.CreateFromCode().Validate([10, 20])

    # ----------------------------------------------------------------------
    def test_ErrorSingleWithNone(self):
        with pytest.raises(
            Exception,
            match=re.escape("None was not expected."),
        ):
            Cardinality.CreateFromCode().Validate(None)

    # ----------------------------------------------------------------------
    def test_ErrorTooFewContainerItems(self):
        with pytest.raises(
            Exception,
            match=re.escape("At least 2 items were expected (1 item was found)."),
        ):
            Cardinality.CreateFromCode(2, 2).Validate([10, ])

    # ----------------------------------------------------------------------
    def test_ErrorTooManyContainerItems(self):
        with pytest.raises(
            Exception,
            match=re.escape("No more than 2 items were expected (3 items were found)."),
        ):
            Cardinality.CreateFromCode(2, 2).Validate([10, 20, 30])
