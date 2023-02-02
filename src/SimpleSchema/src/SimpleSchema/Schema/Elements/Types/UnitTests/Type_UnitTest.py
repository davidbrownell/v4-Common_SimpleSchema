# ----------------------------------------------------------------------
# |
# |  Type_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 11:49:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Type.py"""

import re
import sys

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
    from SimpleSchema.Common.Errors import CardinalityInvalidMetadata
    from SimpleSchema.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
    from SimpleSchema.Schema.Elements.Expressions.ListExpression import ListExpression
    from SimpleSchema.Schema.Elements.Expressions.NoneExpression import NoneExpression
    from SimpleSchema.Schema.Elements.Expressions.StringExpression import Expression, StringExpression

    from SimpleSchema.Schema.Elements.Types.Type import Cardinality, Metadata, Range, Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MyType(Type):
    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                     = "MyType"

    SUPPORTED_PYTHON_TYPES: ClassVar[Optional[Tuple[PythonType, ...]]]      = (str, )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(
        self,
        range_value: Range,
        cardinality: Cardinality,
        metadata: Optional[Metadata],
    ) -> "MyType":
        return MyType(range_value, cardinality, metadata)

    # ----------------------------------------------------------------------
    @overridemethod
    def _ItemToPythonImpl(
        self,
        value: Any,
    ) -> Any:
        return value


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    cardinality_mock = Mock()

    t = MyType(range_mock, cardinality_mock, None)

    assert t.range is range_mock
    assert t.cardinality is cardinality_mock
    assert t.metadata is None

    metadata_mock = Mock()

    t = MyType(range_mock, cardinality_mock, metadata_mock)

    assert t.range is range_mock
    assert t.cardinality is cardinality_mock
    assert t.metadata is metadata_mock


# ----------------------------------------------------------------------
def test_DisplayName():
    assert MyType(Mock(), Cardinality.CreateFromCode(3, 12), None).display_name == "MyType[3, 12]"


# ----------------------------------------------------------------------
def test_Clone():
    range_mock = Mock()
    cardinality_mock = Mock()
    metadata_mock = Mock()

    t = MyType(range_mock, cardinality_mock, metadata_mock).Clone()

    assert t.range is range_mock
    assert t.cardinality is cardinality_mock
    assert t.metadata is metadata_mock

    t = MyType(Mock(), Mock(), None).Clone(
        range=range_mock,
        cardinality=cardinality_mock,
        metadata=metadata_mock,
    )

    assert t.range is range_mock
    assert t.cardinality is cardinality_mock
    assert t.metadata is metadata_mock


# ----------------------------------------------------------------------
def test_Resolve():
    range1 = Range.Create(Path("filename1"), 1, 3, 5, 7)
    range2 = Range.Create(Path("filename2"), 2, 4, 6, 8)

    t = MyType(range1, Mock(), None)

    try:
        with t.Resolve() as resolved_type:
            raise CardinalityInvalidMetadata(range2)
    except SimpleSchemaException as ex:
        assert len(ex.ranges) == 2
        assert ex.ranges[0] is range2
        assert ex.ranges[1] is range1


# ----------------------------------------------------------------------
class TestClassVarErrors(object):
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class MyBadType(Type):
        # ----------------------------------------------------------------------
        @overridemethod
        def _CloneImpl(self, *args, **kwargs):
            raise ValueError("Never Called")

        # ----------------------------------------------------------------------
        @overridemethod
        def _ItemToPythonImpl(self, value: Any) -> Any:
            raise ValueError("Never Called")

    # ----------------------------------------------------------------------
    def test_ErrorName(self):
        with pytest.raises(
            AssertionError,
            match=re.escape("Make sure to define the type's name."),
        ):
            TestClassVarErrors.MyBadType(Mock(), Mock(), None)

    # ----------------------------------------------------------------------
    def test_ErrorSupportedPythonTypes(self):
        # ----------------------------------------------------------------------
        @dataclass(frozen=True)
        class BadType(TestClassVarErrors.MyBadType):
            NAME: ClassVar[str] = "Name"

        # ----------------------------------------------------------------------

        with pytest.raises(
            AssertionError,
            match=re.escape("Make sure to define the supported python types."),
        ):
            BadType(Mock(), Mock(), None)


@dataclass(frozen=True)
class SimpleStringType(Type):
    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = "SimpleString"
    SUPPORTED_PYTHON_TYPES: ClassVar[Optional[Tuple[PythonType, ...]]]      = (str, )

    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(self, *args, **kwargs):
        return SimpleStringType(*args, **kwargs)

    # ----------------------------------------------------------------------
    @overridemethod
    def _ItemToPythonImpl(
        self,
        value: str,
    ) -> str:
        if not value:
            raise Exception("Value is not valid.")

        return value


# ----------------------------------------------------------------------
class TestValidateExpression(object):
    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class NoopType(Type):
        # ----------------------------------------------------------------------
        NAME: ClassVar[str]                                                 = "Noop"
        SUPPORTED_PYTHON_TYPES: ClassVar[Optional[Tuple[PythonType, ...]]]  = None

        # ----------------------------------------------------------------------
        @overridemethod
        def _CloneImpl(self, *args, **kwargs):
            raise Exception("Not implemented")  # pragma: no cover

        # ----------------------------------------------------------------------
        @overridemethod
        def _ValidatePythonItemImpl(self, value: Any) -> None:
            raise Exception("Not implemented")  # pragma: no cover

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class SimpleIntegerType(Type):
        # ----------------------------------------------------------------------
        NAME: ClassVar[str]                                                 = "SimpleInteger"
        SUPPORTED_PYTHON_TYPES: ClassVar[Optional[Tuple[PythonType, ...]]]  = (int, )

        # ----------------------------------------------------------------------
        @overridemethod
        def _CloneImpl(self, *args, **kwargs):
            raise Exception("Not implemented")  # pragma: no cover

        # ----------------------------------------------------------------------
        @overridemethod
        def _ItemToPythonImpl(self, value: Any) -> Any:
            raise Exception("Not implemented")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def test_Single(self):
        assert SimpleStringType(
            Mock(),
            Cardinality.CreateFromCode(),
            None,
        ).ToPython(StringExpression(Mock(), "foo")) == "foo"

    # ----------------------------------------------------------------------
    def test_Optional(self):
        sst = SimpleStringType(
            Mock(),
            Cardinality.CreateFromCode(0, 1),
            None,
        )

        assert sst.ToPython(StringExpression(Mock(), "foo")) == "foo"
        assert sst.ToPython(NoneExpression(Mock())) is None

    # ----------------------------------------------------------------------
    def test_Container(self):
        assert SimpleStringType(
            Mock(),
            Cardinality.CreateFromCode(2, 2),
            None,
        ).ToPython(
            ListExpression(
                Mock(),
                [
                    StringExpression(Mock(), "foo"),
                    StringExpression(Mock(), "bar"),
                ],
            ),
        ) == ["foo", "bar"]

    # ----------------------------------------------------------------------
    def test_ErrorListTypeWithSingleExpression(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("A list of items was expected. (filename <Ln 8, Col 10 -> Ln 12, Col 14>)"),
        ):
            SimpleStringType(
                Mock(),
                Cardinality.CreateFromCode(2, 2),
                None,
            ).ToPython(
                StringExpression(Range.Create(Path("filename"), 8, 10, 12, 14), "foo"),
            )

    # ----------------------------------------------------------------------
    def test_ErrorListTypeWithTooFewExpressions(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("At least 2 items were expected (1 item was found). (filename <Ln 8, Col 10 -> Ln 12, Col 14>)"),
        ):
            SimpleStringType(
                Mock(),
                Cardinality.CreateFromCode(2, 2),
                None,
            ).ToPython(
                ListExpression(
                    Range.Create(Path("filename"), 8, 10, 12, 14),
                    [Mock(), ],
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorListTypeWithTooManyExpressions(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("No more than 2 items were expected (3 items were found). (filename <Ln 8, Col 10 -> Ln 12, Col 14>)"),
        ):
            SimpleStringType(
                Mock(),
                Cardinality.CreateFromCode(2, 2),
                None,
            ).ToPython(
                ListExpression(
                    Range.Create(Path("filename"), 8, 10, 12, 14),
                    [Mock(), Mock(), Mock(), ],
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorSingleTypeWithListExpression(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("A list of items was not expected. (filename <Ln 8, Col 10 -> Ln 12, Col 14>)"),
        ):
            SimpleStringType(
                Mock(),
                Cardinality.CreateFromCode(),
                None,
            ).ToPython(
                ListExpression(
                    Range.Create(Path("filename"), 8, 10, 12, 14),
                    [Mock(), ],
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorSingleTypeWithNoneExpression(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("None was not expected. (filename <Ln 8, Col 10 -> Ln 12, Col 14>)"),
        ):
            SimpleStringType(
                Mock(),
                Cardinality.CreateFromCode(),
                None,
            ).ToPython(
                NoneExpression(Range.Create(Path("filename"), 8, 10, 12, 14)),
            )

    # ----------------------------------------------------------------------
    def test_ErrorSingleTypeWrongExpression(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("A python 'int' value cannot be converted into a 'SimpleString' type. (filename <Ln 8, Col 10 -> Ln 12, Col 14>)"),
        ):
            SimpleStringType(
                Mock(),
                Cardinality.CreateFromCode(),
                None,
            ).ToPython(
                IntegerExpression(
                    Range.Create(Path("filename"), 8, 10, 12, 14),
                    10,
                ),
            )

    # ----------------------------------------------------------------------
    def test_ErrorWrongPythonType(self):
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("A python 'str' value cannot be converted into a 'SimpleInteger' type. (filename <Ln 8, Col 10 -> Ln 12, Col 14>)"),
        ):
            TestValidateExpression.SimpleIntegerType(
                Mock(),
                Cardinality.CreateFromCode(),
                None,
            ).ToPython(
                StringExpression(
                    Range.Create(Path("filename"), 8, 10, 12, 14),
                    "foo",
                ),
            )


# ----------------------------------------------------------------------
class TestValidatePython(object):
    # ----------------------------------------------------------------------
    def test_Single(self):
        assert SimpleStringType(
            Mock(),
            Cardinality.CreateFromCode(),
            None,
        ).ToPython("foo") == "foo"

    # ----------------------------------------------------------------------
    def test_Optional(self):
        sst = SimpleStringType(
            Mock(),
            Cardinality.CreateFromCode(0, 1),
            None,
        )

        assert sst.ToPython("foo") == "foo"
        assert sst.ToPython(None) is None

    # ----------------------------------------------------------------------
    def test_Container(self):
        assert SimpleStringType(
            Mock(),
            Cardinality.CreateFromCode(2, 2),
            None,
        ).ToPython(["one", "two", ]) == ["one", "two"]
