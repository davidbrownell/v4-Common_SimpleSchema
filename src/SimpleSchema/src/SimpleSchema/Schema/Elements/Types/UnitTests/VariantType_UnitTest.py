# ----------------------------------------------------------------------
# |
# |  VariantType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 12:11:54
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for VariantType.py"""

import re
import sys

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Tuple, Type as PythonType
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Types import overridemethod


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Common.Range import Range
    from SimpleSchema.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality

    from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
    from SimpleSchema.Schema.Elements.Expressions.ListExpression import ListExpression
    from SimpleSchema.Schema.Elements.Expressions.NumberExpression import NumberExpression
    from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression

    from SimpleSchema.Schema.Elements.Types.VariantType import Type, VariantType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    cardinality_mock = Mock()
    metadata_mock = Mock()
    types_mock = [Mock(), Mock()]

    v = VariantType(range_mock, cardinality_mock, metadata_mock, types_mock)  # type: ignore

    assert v.range is range_mock
    assert v.cardinality is cardinality_mock
    assert v.metadata is metadata_mock
    assert v.types is types_mock


# ----------------------------------------------------------------------
def test_VariantCardinality():
    child_type_mock1 = Mock()
    child_type_mock1.cardinality = Cardinality.CreateFromCode()

    child_type_mock2 = Mock()
    child_type_mock2.cardinality = Cardinality.CreateFromCode()

    VariantType(
        Mock(),
        Cardinality.CreateFromCode(0, 1),
        None,
        [child_type_mock1, child_type_mock2],
    )


# ----------------------------------------------------------------------
def test_ElementCardinality():
    child_type_mock1 = Mock()
    child_type_mock1.cardinality = Cardinality.CreateFromCode(0, 1)

    child_type_mock2 = Mock()
    child_type_mock2.cardinality = Cardinality.CreateFromCode(5, 5)

    VariantType(
        Mock(),
        Cardinality.CreateFromCode(),
        None,
        [child_type_mock1, child_type_mock2],
    )


# ----------------------------------------------------------------------
def test_DisplayName():
    type1 = Mock()
    type1.display_name = "Type1"

    type2 = Mock()
    type2.display_name = "Type2"

    type3 = Mock()
    type3.display_name = "Type3"

    assert VariantType(
        Mock(),
        Cardinality.CreateFromCode(3, 3),
        None,
        [type1, type2],
    ).display_name == "(Type1 | Type2)[3]"

    assert VariantType(
        Mock(),
        Cardinality.CreateFromCode(),
        None,
        [type1, type2, type3],
    ).display_name == "(Type1 | Type2 | Type3)"


# ----------------------------------------------------------------------
def test_ValidateChildCardinalityPython():
    vt = VariantType(
        Mock(),
        Cardinality.CreateFromCode(),
        None,
        [
            _SimpleStringType(
                Mock(),
                Cardinality.CreateFromCode(2, 2),
                None,
            ),
            _SimpleIntegerType(
                Mock(),
                Cardinality.CreateFromCode(0, 1),
                None,
            ),
        ],
    )

    assert vt.ToPython(["one", "two"]) == ["one", "two"]
    assert vt.ToPython(10) == 10
    assert vt.ToPython(None) is None


# ----------------------------------------------------------------------
def test_ValidateParentCardinalityPython():
    vt = VariantType(
        Mock(),
        Cardinality.CreateFromCode(2, 2),
        None,
        [
            _SimpleStringType(
                Mock(),
                Cardinality.CreateFromCode(),
                None,
            ),
            _SimpleIntegerType(
                Mock(),
                Cardinality.CreateFromCode(),
                None,
            ),
        ],
    )

    assert vt.ToPython(["one", "two"]) == ["one", "two"]
    assert vt.ToPython([10, 20]) == [10, 20]
    assert vt.ToPython(["one", 20]) == ["one", 20]


# ----------------------------------------------------------------------
def test_ValidateExpressionParentCardinality():
    vt = VariantType(
        Mock(),
        Cardinality.CreateFromCode(2, 2),
        None,
        [
            _SimpleStringType(
                Mock(),
                Cardinality.CreateFromCode(),
                None,
            ),
            _SimpleIntegerType(
                Mock(),
                Cardinality.CreateFromCode(),
                None,
            ),
        ],
    )

    assert vt.ToPython(
        ListExpression(
            Mock(),
            [
                StringExpression(Mock(), "one"),
                StringExpression(Mock(), "two"),
            ],
        ),
    ) == ["one", "two"]


# ----------------------------------------------------------------------
def test_ValidateExpressionChildCardinality():
    vt = VariantType(
        Mock(),
        Cardinality.CreateFromCode(),
        None,
        [
            _SimpleStringType(
                Mock(),
                Cardinality.CreateFromCode(2, 2),
                None,
            ),
            _SimpleIntegerType(
                Mock(),
                Cardinality.CreateFromCode(3, 3),
                None,
            ),
        ],
    )

    assert vt.ToPython(
        ListExpression(
            Mock(),
            [
                StringExpression(Mock(), "one"),
                StringExpression(Mock(), "two"),
            ],
        ),
    ) == ["one", "two"]

    assert vt.ToPython(
        ListExpression(
            Mock(),
            [
                IntegerExpression(Mock(), 10),
                IntegerExpression(Mock(), 20),
                IntegerExpression(Mock(), 30),
            ],
        ),
    ) == [10, 20, 30]


# ----------------------------------------------------------------------
def test_ErrorNotEnoughTypes():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("At least two types must be provided. (bad variant <Ln 10, Col 11 -> Ln 12, Col 13>)"),
    ):
        VariantType(
            Range.Create(Path("bad variant"), 10, 11, 12, 13),
            Mock(),
            None,
            [Mock(), ],
        )


# ----------------------------------------------------------------------
def test_ErrorNested():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Variant types may not be nested within variant types. (the bad file <Ln 100, Col 200 -> Ln 300, Col 400>)"),
    ):
        VariantType(
            Mock(),
            Mock(),
            None,
            [
                Mock(),
                VariantType(
                    Range.Create(Path("the bad file"), 100, 200, 300, 400),
                    Mock(),
                    None,
                    [Mock(), Mock(), ],
                ),
                Mock(),
            ],
        )


# ----------------------------------------------------------------------
def test_ErrorElementCardinality():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Types nested within a variant cannot specify cardinality when the variant specifies cardinality as well; either remove cardinality values from all nested items or remove the cardinality from the variant itself. (filename <Ln 100, Col 200 -> Ln 300, Col 400>)"),
    ):
        element1_mock = Mock()
        element1_mock.cardinality = Cardinality.CreateFromCode()

        element2_mock = Mock()
        element2_mock.cardinality = Cardinality.CreateFromCode(2, 2)

        object.__setattr__(
            element2_mock.cardinality,
            "range",
            Range.Create(Path("filename"), 100, 200, 300, 400),
        )

        VariantType(
            Mock(),
            Cardinality.CreateFromCode(0, 1),
            None,
            [element1_mock, element2_mock, ],
        )


# ----------------------------------------------------------------------
def test_ErrorNoMatchesPython():
    with pytest.raises(
        Exception,
        match=re.escape("The python 'float' value does not correspond to any types within '(SimpleString | SimpleInteger)"),
    ):
        VariantType(
            Mock(),
            Cardinality.CreateFromCode(),
            None,
            [
                _SimpleStringType(Mock(), Cardinality.CreateFromCode(), None),
                _SimpleIntegerType(Mock(), Cardinality.CreateFromCode(), None),
            ],
        ).ToPython(3.14)


# ----------------------------------------------------------------------
def test_ErrorNoMatchesExpression():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("The python 'float' value does not correspond to any types within '(SimpleString | SimpleInteger)'. (filename <Ln 100, Col 200 -> Ln 300, Col 400>)"),
    ):
        VariantType(
            Mock(),
            Cardinality.CreateFromCode(),
            None,
            [
                _SimpleStringType(Mock(), Cardinality.CreateFromCode(), None),
                _SimpleIntegerType(Mock(), Cardinality.CreateFromCode(), None),
            ],
        ).ToPython(
            NumberExpression(
                Range.Create(Path("filename"), 100, 200, 300, 400),
                3.14,
            ),
        )


# ----------------------------------------------------------------------
def test_ErrorNoMatchesExpressionChildCardinality():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("The expression 'List' does not produce a value that corresponds to any types within '(SimpleString[2] | SimpleInteger)'. (filename <Ln 100, Col 200 -> Ln 300, Col 400>)"),
    ):
        VariantType(
            Mock(),
            Cardinality.CreateFromCode(),
            None,
            [
                _SimpleStringType(Mock(), Cardinality.CreateFromCode(2, 2), None),
                _SimpleIntegerType(Mock(), Cardinality.CreateFromCode(), None),
            ],
        ).ToPython(
            ListExpression(
                Range.Create(Path("filename"), 100, 200, 300, 400),
                [
                    NumberExpression(Mock(), 3.14),
                ],
            ),
        )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _SimpleStringType(Type):
    NAME: ClassVar[str]                                                     = "SimpleString"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                 = (str, )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _ItemToPythonImpl(
        self,
        value: str,
    ) -> str:
        if not value:
            raise ValueError("Invalid simple string value")

        return value


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _SimpleIntegerType(Type):
    NAME: ClassVar[str]                                                     = "SimpleInteger"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                 = (int, )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _ItemToPythonImpl(
        self,
        value: int,
    ) -> int:
        if not value:
            raise ValueError("Invalid simple integer value")

        return value
