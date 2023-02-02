# ----------------------------------------------------------------------
# |
# |  TupleType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 10:43:08
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for TupleType.py"""

import re
import sys
import textwrap

from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Optional, Tuple, Type as PythonType
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
    from SimpleSchema.Schema.Elements.Expressions.NoneExpression import NoneExpression
    from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression
    from SimpleSchema.Schema.Elements.Expressions.TupleExpression import TupleExpression

    from SimpleSchema.Schema.Elements.Types.TupleType import TupleType, Type


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    cardinality_mock = Mock()
    metadata_mock = Mock()
    types_mock = [Mock(), ]

    tt = TupleType(range_mock, cardinality_mock, metadata_mock, types_mock)  # type: ignore

    assert tt.range is range_mock
    assert tt.cardinality is cardinality_mock
    assert tt.metadata is metadata_mock
    assert tt.types is types_mock


# ----------------------------------------------------------------------
def test_DisplayName():
    one_type = Mock()
    one_type.display_name = "One"

    assert TupleType(
        Mock(),
        Cardinality.CreateFromCode(0, 1),
        None,
        [
            one_type,
        ],
    ).display_name == "(One, )?"

    two_type = Mock()
    two_type.display_name = "Two"

    three_type = Mock()
    three_type.display_name = "Three"

    assert TupleType(
        Mock(),
        Cardinality.CreateFromCode(0),
        None,
        [
            one_type,
            two_type,
            three_type,
        ],
    ).display_name == "(One, Two, Three, )*"


# ----------------------------------------------------------------------
def test_Clone():
    range_mock = Mock()
    cardinality_mock = Mock()
    metadata_mock = Mock()
    types = [Mock(), Mock(), ]

    tt = TupleType(range_mock, cardinality_mock, metadata_mock, types)  # type: ignore

    assert tt.Clone() == tt


# ----------------------------------------------------------------------
def test_ErrorNoTypes():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("No types were provided. (bad file <Ln 1, Col 2 -> Ln 3, Col 4>)"),
    ):
        TupleType(Range.Create(Path("bad file"), 1, 2, 3, 4), Mock(), None, [])


# ----------------------------------------------------------------------
class TestToPython(object):
    # ----------------------------------------------------------------------
    def test_Standard(self, _tuple_type):
        assert _tuple_type.ToPython(("one", [10, 20], "last")) == ("one", [10, 20], "last")
        assert _tuple_type.ToPython(("one", [10, 20], None)) == ("one", [10, 20], None)

        assert _tuple_type.ToPython(
            TupleExpression(
                Mock(),
                (
                    StringExpression(Mock(), "one"),
                    ListExpression(
                        Mock(),
                        [
                            IntegerExpression(Mock(), 10),
                            IntegerExpression(Mock(), 20),
                        ],
                    ),
                    NoneExpression(Mock()),
                ),
            ),
        ) == ("one", [10, 20], None)

    # ----------------------------------------------------------------------
    def test_Nested(self, _nested_tuple_type):
        assert _nested_tuple_type.ToPython([("one", ([10, 20], ("two", )))]) == [("one", ([10, 20], ("two", )))]

        assert _nested_tuple_type.ToPython(
            [
                ("one", ([10, 20], ("two", ))),
                ("three", ([30, 40], ("four", ))),
            ],
        ) == [
            ("one", ([10, 20], ("two", ))),
            ("three", ([30, 40], ("four", ))),
        ]

        assert _nested_tuple_type.ToPython(
            ListExpression(
                Mock(),
                [
                    TupleExpression(
                        Mock(),
                        (
                            StringExpression(Mock(), "one"),
                            TupleExpression(
                                Mock(),
                                (
                                    ListExpression(
                                        Mock(),
                                        [
                                            IntegerExpression(Mock(), 10),
                                            IntegerExpression(Mock(), 20),
                                        ],
                                    ),
                                    TupleExpression(
                                        Mock(),
                                        (
                                            StringExpression(Mock(), "two"),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ],
            ),
        ) == [("one", ([10, 20], ("two", )))]

    # ----------------------------------------------------------------------
    def test_ErrorNotEnoughItemsPython(self, _tuple_type):
        with pytest.raises(
            Exception,
            match=re.escape("3 tuple items were expected (1 tuple item was found)."),
        ):
            _tuple_type.ToPython(("one", ))

    # ----------------------------------------------------------------------
    def test_ErrorNotEnoughItemsExpression(self, _tuple_type):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("3 tuple items were expected (1 tuple item was found). (filename <Ln 100, Col 200 -> Ln 300, Col 400>)"),
        ):
            _tuple_type.ToPython(
                TupleExpression(
                    Range.Create(Path("filename"), 100, 200, 300, 400),
                    (
                        StringExpression(Mock(), "one"),
                    ),
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorTooManyItemsPython(self, _tuple_type):
        with pytest.raises(
            Exception,
            match=re.escape("3 tuple items were expected (4 tuple items were found)."),
        ):
            _tuple_type.ToPython(("one", [10, 20], "last", "too many"))

    # ----------------------------------------------------------------------
    def test_ErrorTooManyItemsExpression(self, _tuple_type):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("3 tuple items were expected (4 tuple items were found). (filename <Ln 100, Col 200 -> Ln 300, Col 400>)"),
        ):
            _tuple_type.ToPython(
                TupleExpression(
                    Range.Create(Path("filename"), 100, 200, 300, 400),
                    (
                        StringExpression(Mock(), "one"),
                        ListExpression(Mock(), [IntegerExpression(Mock(), 10), IntegerExpression(Mock(), 20)]),
                        NoneExpression(Mock()),
                        StringExpression(Mock(), "too many"),
                    ),
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorInvalidCardinalityPython(self, _tuple_type):
        with pytest.raises(
            Exception,
            match=re.escape("At least 2 items were expected (1 item was found)."),
        ):
            _tuple_type.ToPython(("one", [10, ], None))

    # ----------------------------------------------------------------------
    def test_ErrorInvalidCardinalityExpression(self, _tuple_type):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                textwrap.dedent(
                    """\
                    At least 2 items were expected (1 item was found).

                        - filename2 <Ln 1, Col 2 -> Ln 3, Col 4>
                        - filename1 <Ln 100, Col 200 -> Ln 300, Col 400>
                    """,
                ),
            ),
        ):
            _tuple_type.ToPython(
                TupleExpression(
                    Range.Create(Path("filename1"), 100, 200, 300, 400),
                    (
                        StringExpression(Mock(), "one"),
                        ListExpression(
                            Range.Create(Path("filename2"), 1, 2, 3, 4),
                            [
                                IntegerExpression(Mock(), 10),
                            ],
                        ),
                        NoneExpression(Mock()),
                    ),
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorInvalidExpressionType(self, _tuple_type):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("A tuple expression was expected. (filename <Ln 2, Col 4 -> Ln 6, Col 8>)"),
        ):
            _tuple_type.ToPython(
                IntegerExpression(Range.Create(Path("filename"), 2, 4, 6, 8), 10),
            )

    # ----------------------------------------------------------------------
    def test_ErrorInvalidItemExpression(self, _tuple_type):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                textwrap.dedent(
                    """\
                    Empty string

                        - filename2 <Ln 1, Col 2 -> Ln 3, Col 4>
                        - filename1 <Ln 100, Col 200 -> Ln 300, Col 400>
                    """,
                ),
            ),
        ):
            _tuple_type.ToPython(
                TupleExpression(
                    Range.Create(Path("filename1"), 100, 200, 300, 400),
                    (
                        StringExpression(Mock(), "one"),
                        ListExpression(
                            Mock(),
                            [
                                IntegerExpression(Mock(), 10),
                                IntegerExpression(Mock(), 20),
                            ],
                        ),
                        StringExpression(
                            Range.Create(Path("filename2"), 1, 2, 3, 4),
                            "",
                        ),
                    ),
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorInvalidItemPython(self, _tuple_type):
        with pytest.raises(
            Exception,
            match=re.escape("Empty string"),
        ):
            _tuple_type.ToPython(("one", [10, 20], ""))

    # ----------------------------------------------------------------------
    def test_ErrorNestedListItemExpression(self, _nested_tuple_type):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                textwrap.dedent(
                    """\
                    At least 2 items were expected (1 item was found).

                        - filename1 <Ln 1, Col 2 -> Ln 3, Col 4>
                        - filename2 <Ln 10, Col 20 -> Ln 30, Col 40>
                        - filename3 <Ln 100, Col 200 -> Ln 300, Col 400>
                        - filename4 <Ln 1000, Col 2000 -> Ln 3000, Col 4000>
                    """,
                ),
            ),
        ):
            _nested_tuple_type.ToPython(
                ListExpression(
                    Range.Create(Path("filename4"), 1000, 2000, 3000, 4000),
                    [
                        TupleExpression(
                            Range.Create(Path("filename3"), 100, 200, 300, 400),
                            (
                                StringExpression(Mock(), "one"),
                                TupleExpression(
                                    Range.Create(Path("filename2"), 10, 20, 30, 40),
                                    (
                                        ListExpression(
                                            Range.Create(Path("filename1"), 1, 2, 3, 4),
                                            [
                                                IntegerExpression(Mock(), 10),
                                                # IntegerExpression(Mock(), 20),
                                            ],
                                        ),
                                        TupleExpression(
                                            Mock(),
                                            (
                                                StringExpression(Mock(), "two"),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ],
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorNestedListItemPython(self, _nested_tuple_type):
        with pytest.raises(
            Exception,
            match=re.escape("At least 2 items were expected (1 item was found)."),
        ):
            _nested_tuple_type.ToPython(
                [
                    ("one", ([10, ], ("two", ))),
                ],
            )

    # ----------------------------------------------------------------------
    def test_ErrorNestedInvalidStringExpression(self, _nested_tuple_type):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape(
                textwrap.dedent(
                    """\
                    Empty string

                        - filename1 <Ln 1, Col 2 -> Ln 3, Col 4>
                        - filename2 <Ln 10, Col 20 -> Ln 30, Col 40>
                        - filename3 <Ln 100, Col 200 -> Ln 300, Col 400>
                        - filename4 <Ln 1000, Col 2000 -> Ln 3000, Col 4000>
                        - filename5 <Ln 10000, Col 20000 -> Ln 30000, Col 40000>
                    """,
                ),
            ),
        ):
            _nested_tuple_type.ToPython(
                ListExpression(
                    Range.Create(Path("filename5"), 10000, 20000, 30000, 40000),
                    [
                        TupleExpression(
                            Range.Create(Path("filename4"), 1000, 2000, 3000, 4000),
                            (
                                StringExpression(Mock(), "one"),
                                TupleExpression(
                                    Range.Create(Path("filename3"), 100, 200, 300, 400),
                                    (
                                        ListExpression(
                                            Mock(),
                                            [
                                                IntegerExpression(Mock(), 10),
                                                IntegerExpression(Mock(), 20),
                                            ],
                                        ),
                                        TupleExpression(
                                            Range.Create(Path("filename2"), 10, 20, 30, 40),
                                            (
                                                StringExpression(
                                                    Range.Create(Path("filename1"), 1, 2, 3, 4),
                                                    "",
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ],
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorNestedInvalidStringPython(self, _nested_tuple_type):
        with pytest.raises(
            Exception,
            match=re.escape("Empty string"),
        ):
            _nested_tuple_type.ToPython(
                [
                    ("one", ([10, 20], ("", ))),
                ],
            )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class _SimpleStringType(Type):
        NAME: ClassVar[str]                                                 = "SimpleString"
        SUPPORTED_PYTHON_TYPES: ClassVar[Optional[Tuple[PythonType, ...]]]  = (str, )

        # ----------------------------------------------------------------------
        @overridemethod
        def _CloneImpl(self, *args, **kwargs):
            return TestToPython._SimpleStringType(*args, **kwargs)

        # ----------------------------------------------------------------------
        @overridemethod
        def _ItemToPythonImpl(
            self,
            value: str,
        ) -> str:
            if not value:
                raise ValueError("Empty string")

            return value

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class _SimpleIntegerType(Type):
        NAME: ClassVar[str]                                                 = "SimpleInteger"
        SUPPORTED_PYTHON_TYPES: ClassVar[Optional[Tuple[PythonType, ...]]]  = (int, )

        # ----------------------------------------------------------------------
        @overridemethod
        def _CloneImpl(self, *args, **kwargs):
            return TestToPython._SimpleIntegerType(*args, **kwargs)

        # ----------------------------------------------------------------------
        @overridemethod
        def _ItemToPythonImpl(
            self,
            value: int,
        ) -> int:
            if value < 0:
                raise ValueError("Negative integer.")

            return value

    # ----------------------------------------------------------------------
    @classmethod
    @pytest.fixture
    def _tuple_type(cls):
        return TupleType(
            Mock(),
            Cardinality.CreateFromCode(),
            None,
            [
                cls._SimpleStringType(Mock(), Cardinality.CreateFromCode(), None),
                cls._SimpleIntegerType(Mock(), Cardinality.CreateFromCode(2, 2), None),
                cls._SimpleStringType(Mock(), Cardinality.CreateFromCode(0, 1), None),
            ],
        )

    # ----------------------------------------------------------------------
    @classmethod
    @pytest.fixture
    def _nested_tuple_type(cls):
        # (String, (Integer[2], (String, )))+
        return TupleType(
            Mock(),
            Cardinality.CreateFromCode(1),
            None,
            [
                cls._SimpleStringType(Mock(), Cardinality.CreateFromCode(), None),
                TupleType(
                    Mock(),
                    Cardinality.CreateFromCode(),
                    None,
                    [
                        cls._SimpleIntegerType(Mock(), Cardinality.CreateFromCode(2, 2), None),
                        TupleType(
                            Mock(),
                            Cardinality.CreateFromCode(),
                            None,
                            [
                                cls._SimpleStringType(Mock(), Cardinality.CreateFromCode(), None),
                            ],
                        ),
                    ],
                ),
            ],
        )
