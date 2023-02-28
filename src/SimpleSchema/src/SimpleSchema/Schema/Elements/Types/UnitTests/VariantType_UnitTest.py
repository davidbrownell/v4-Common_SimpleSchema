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
import textwrap

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

    from SimpleSchema.Schema.Elements.Types.BasicType import BasicType
    from SimpleSchema.Schema.Elements.Types.ReferenceType import ReferenceType
    from SimpleSchema.Schema.Elements.Types.VariantType import VariantType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    types_mock = [Mock(), Mock()]

    v = VariantType(range_mock, types_mock)  # type: ignore

    assert v.range is range_mock
    assert v.types is types_mock


# ----------------------------------------------------------------------
def test_ElementCardinality():
    VariantType(
        Mock(),
        [
            ReferenceType.Create(Mock(), Mock(), Mock(), _SimpleStringType(Mock()), Cardinality.CreateFromCode(0, 1), None),
            ReferenceType.Create(Mock(), Mock(), Mock(), _SimpleStringType(Mock()), Cardinality.CreateFromCode(5, 5), None),
        ],
    )


# ----------------------------------------------------------------------
def test_DisplayType():
    type1 = Mock()
    type1.display_type = "Type1"

    type2 = Mock()
    type2.display_type = "Type2[2]"

    type3 = Mock()
    type3.display_type = "Type3 {constraint}"

    assert VariantType(Mock(),[type1, type2]).display_type == "(Type1 | Type2[2])"
    assert VariantType(Mock(), [type1, type2, type3]).display_type == "(Type1 | Type2[2] | <Type3 {constraint}>)"


# ----------------------------------------------------------------------
def test_ReferenceTypeToPython():
    rt = ReferenceType.Create(
        Mock(),
        Mock(),
        Mock(),
        VariantType(
            Mock(),
            [
                ReferenceType.Create(
                    Mock(),
                    Mock(),
                    Mock(),
                    _SimpleStringType(Mock()),
                    Cardinality.CreateFromCode(),
                    None,
                ),
                ReferenceType.Create(
                    Mock(),
                    Mock(),
                    Mock(),
                    _SimpleIntegerType(Mock()),
                    Cardinality.CreateFromCode(),
                    None,
                ),
            ],
        ),
        Cardinality.CreateFromCode(2, 2),
        None,
    )

    assert rt.ToPython(["foo", "bar"]) == ["foo", "bar"]
    assert rt.ToPython([123, 456]) == [123, 456]


# ----------------------------------------------------------------------
def test_ReferenceTypeToPythonWithChildCardinality():
    rt = ReferenceType(
        Mock(),
        VariantType(
            Mock(),
            [
                ReferenceType(
                    Mock(),
                    _SimpleStringType(Mock()),
                    Mock(),
                    Mock(),
                    Cardinality.CreateFromCode(2, 2),
                    None,
                    force_single_cardinality=False,
                    was_dynamically_generated=False,
                ),
                ReferenceType(
                    Mock(),
                    _SimpleIntegerType(Mock()),
                    Mock(),
                    Mock(),
                    Cardinality.CreateFromCode(2, 2),
                    None,
                    force_single_cardinality=False,
                    was_dynamically_generated=False,
                ),
            ],
        ),
        Mock(),
        Mock(),
        Cardinality.CreateFromCode(3, 3),
        None,
        force_single_cardinality=False,
        was_dynamically_generated=False,
    )

    assert rt.ToPython(
            [
                ["foo", "bar"],
                [1, 2],
                [3, 4],
            ],
        ) == [
            ["foo", "bar"],
            [1, 2],
            [3, 4],
        ]


# ----------------------------------------------------------------------
def test_ValidateChildCardinalityPython():
    vt = VariantType(
        Mock(),
        [
            ReferenceType.Create(
                Mock(),
                Mock(),
                Mock(),
                _SimpleStringType(Mock()),
                Cardinality.CreateFromCode(2, 2),
                None,
            ),
            ReferenceType.Create(
                Mock(),
                Mock(),
                Mock(),
                _SimpleIntegerType(Mock()),
                Cardinality.CreateFromCode(0, 1),
                None,
            ),
        ],
    )

    assert vt.ToPython(["one", "two"]) == ["one", "two"]
    assert vt.ToPython(10) == 10
    assert vt.ToPython(None) is None


# ----------------------------------------------------------------------
def test_ValidateExpressionChildCardinality():
    vt = VariantType(
        Mock(),
        [
            ReferenceType.Create(
                Mock(),
                Mock(),
                Mock(),
                _SimpleStringType(Mock()),
                Cardinality.CreateFromCode(2, 2),
                None,
            ),
            ReferenceType.Create(
                Mock(),
                Mock(),
                Mock(),
                _SimpleIntegerType(Mock()),
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
def test_ToPythonSubtleCardinality():
    rt = ReferenceType.Create(
        Mock(),
        Mock(),
        Mock(),
        VariantType(
            Mock(),
            [
                ReferenceType.Create(
                    Mock(),
                    Mock(),
                    Mock(),
                    _SimpleIntegerType(Mock()),
                    Cardinality.CreateFromCode(),
                    None,
                ),
                ReferenceType.Create(
                    Mock(),
                    Mock(),
                    Mock(),
                    _SimpleStringType(Mock()),
                    Cardinality.CreateFromCode(3, 3),
                    None,
                ),
            ],
        ),
        Cardinality.CreateFromCode(),
        None,
    )

    assert rt.ToPython(["foo", "bar", "baz"],) == ["foo", "bar", "baz", ]
    assert rt.ToPython(123) == 123


# ----------------------------------------------------------------------
def test_ErrorNotEnoughTypes():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("At least two types must be provided. (bad variant <Ln 10, Col 11 -> Ln 12, Col 13>)"),
    ):
        VariantType(
            Range.Create(Path("bad variant"), 10, 11, 12, 13),
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
            [
                Mock(),
                VariantType(
                    Range.Create(Path("the bad file"), 100, 200, 300, 400),
                    [Mock(), Mock(), ],
                ),
                Mock(),
            ],
        )


# ----------------------------------------------------------------------
def test_ErrorNoMatchesPython():
    with pytest.raises(
        Exception,
        match=re.escape("A 'float' value does not correspond to any types within '(SimpleString | SimpleInteger)"),
    ):
        VariantType(
            Mock(),
            [
                ReferenceType.Create(Mock(), Mock(), Mock(), _SimpleStringType(Mock()), Cardinality.CreateFromCode(), None),
                ReferenceType.Create(Mock(), Mock(), Mock(), _SimpleIntegerType(Mock()), Cardinality.CreateFromCode(), None),
            ],
        ).ToPython(3.14)


# ----------------------------------------------------------------------
def test_ErrorNoMatchesExpression():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape(
            textwrap.dedent(
                """\
                A 'float' value does not correspond to any types within '(SimpleString | SimpleInteger)'.

                    Additional Information:
                        SimpleString
                            A 'float' value cannot be converted to a 'SimpleString' type. (filename <Ln 1, Col 2 -> Ln 3, Col 4>)

                        SimpleInteger
                            A 'float' value cannot be converted to a 'SimpleInteger' type. (filename <Ln 11, Col 22 -> Ln 33, Col 44>)

                    - filename <Ln 100, Col 200 -> Ln 300, Col 400>
                """,
            ),
        ),
    ):
        VariantType(
            Mock(),
            [
                ReferenceType.Create(Range.Create(Path("filename"), 1, 2, 3, 4), Mock(), Mock(), _SimpleStringType(Mock()), Cardinality.CreateFromCode(), None),
                ReferenceType.Create(Range.Create(Path("filename"), 11, 22, 33, 44), Mock(), Mock(), _SimpleIntegerType(Mock()), Cardinality.CreateFromCode(), None),
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
        match=re.escape(
            textwrap.dedent(
                """\
                A 'list' value does not correspond to any types within '(SimpleString[2] | SimpleInteger)'.

                    Additional Information:
                        SimpleString[2]
                            At least 2 items were expected (1 item was found). (filename <Ln 1, Col 2 -> Ln 3, Col 4>)

                        SimpleInteger
                            A list of items was not expected. (filename <Ln 10, Col 20 -> Ln 30, Col 40>)

                    - filename <Ln 100, Col 200 -> Ln 300, Col 400>
                """,
            ),
        ),
    ):
        VariantType(
            Mock(),
            [
                ReferenceType.Create(Range.Create(Path("filename"), 1, 2, 3, 4), Mock(), Mock(), _SimpleStringType(Mock()), Cardinality.CreateFromCode(2, 2), None),
                ReferenceType.Create(Range.Create(Path("filename"), 10, 20, 30, 40), Mock(), Mock(), _SimpleIntegerType(Mock()), Cardinality.CreateFromCode(), None),
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
def test_ErrorNoMatchesExpressionChildCardinalityViaReferenceType():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape(
            textwrap.dedent(
                """\
                A 'list' value does not correspond to any types within '(SimpleString[2] | SimpleInteger)'.

                    Additional Information:
                        SimpleString[2]
                            At least 2 items were expected (1 item was found). (filename <Ln 1, Col 2 -> Ln 3, Col 4>)

                        SimpleInteger
                            A list of items was not expected. (filename <Ln 10, Col 20 -> Ln 30, Col 40>)

                    - filename <Ln 100, Col 200 -> Ln 300, Col 400>
                    - filename <Ln 1, Col 2 -> Ln 3, Col 4>
                """,
            ),
        ),
    ):
        ReferenceType.Create(
            Range.Create(Path("filename"), 1, 2, 3, 4),
            Mock(),
            Mock(),
            VariantType(
                Mock(),
                [
                    ReferenceType.Create(Range.Create(Path("filename"), 1, 2, 3, 4), Mock(), Mock(), _SimpleStringType(Mock()), Cardinality.CreateFromCode(2, 2), None),
                    ReferenceType.Create(Range.Create(Path("filename"), 10, 20, 30, 40), Mock(), Mock(), _SimpleIntegerType(Mock()), Cardinality.CreateFromCode(), None),
                ],
            ),
            Cardinality.CreateFromCode(),
            None,
        ).ToPython(
            ListExpression(
                Range.Create(Path("filename"), 100, 200, 300, 400),
                [
                    NumberExpression(Mock(), 3.14),
                ],
            ),
        )


# ----------------------------------------------------------------------
def test_ErrorNoMatchesExpressionViaReferenceType():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape(
            textwrap.dedent(
                """\
                A 'float' value does not correspond to any types within '(SimpleString | SimpleInteger)'.

                    Additional Information:
                        SimpleString
                            A 'float' value cannot be converted to a 'SimpleString' type. (filename <Ln 11, Col 22 -> Ln 33, Col 44>)

                        SimpleInteger
                            A 'float' value cannot be converted to a 'SimpleInteger' type. (filename <Ln 111, Col 222 -> Ln 333, Col 444>)

                    - filename <Ln 100, Col 200 -> Ln 300, Col 400>
                    - filename <Ln 1, Col 2 -> Ln 3, Col 4>
                """,
            ),
        ),
    ):
        ReferenceType.Create(
            Range.Create(Path("filename"), 1, 2, 3, 4),
            Mock(),
            Mock(),
            VariantType(
                Mock(),
                [
                    ReferenceType.Create(Range.Create(Path("filename"), 11, 22, 33, 44), Mock(), Mock(), _SimpleStringType(Mock()), Cardinality.CreateFromCode(), None),
                    ReferenceType.Create(Range.Create(Path("filename"), 111, 222, 333, 444), Mock(), Mock(), _SimpleIntegerType(Mock()), Cardinality.CreateFromCode(), None),
                ],
            ),
            Cardinality.CreateFromCode(),
            None,
        ).ToPython(NumberExpression(Range.Create(Path("filename"), 100, 200, 300, 400), 3.14))

# ----------------------------------------------------------------------
def test_ReferenceCount():
    t1 = Mock()
    t2 = Mock()

    tt = VariantType(Mock(), [t1, t2])

    assert tt.reference_count == 0
    assert t1.Increment.call_count == 0
    assert t2.Increment.call_count == 0

    tt.Increment()
    assert tt.reference_count == 1
    assert t1.Increment.call_count == 1
    assert t2.Increment.call_count == 1

    tt.Increment()
    assert tt.reference_count == 2
    assert t1.Increment.call_count == 2
    assert t2.Increment.call_count == 2

    tt.Increment(shallow=True)
    assert tt.reference_count == 3
    assert t1.Increment.call_count == 2
    assert t2.Increment.call_count == 2


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _SimpleStringType(BasicType):
    NAME: ClassVar[str]                                                     = "SimpleString"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                 = (str, )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _ToPythonImpl(
        self,
        value: str,
    ) -> str:
        if not value:
            raise ValueError("Invalid simple string value")

        return value


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _SimpleIntegerType(BasicType):
    NAME: ClassVar[str]                                                     = "SimpleInteger"
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                 = (int, )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _ToPythonImpl(
        self,
        value: int,
    ) -> int:
        if not value:
            raise ValueError("Invalid simple integer value")

        return value
