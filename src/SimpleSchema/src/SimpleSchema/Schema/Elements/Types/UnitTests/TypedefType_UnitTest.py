# ----------------------------------------------------------------------
# |
# |  TypedefType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 11:07:54
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for TypedefType.py"""

import re
import sys
import textwrap

from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Common.Errors import CardinalityInvalidMetadata
    from SimpleSchema.Common.Range import Range
    from SimpleSchema.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
    from SimpleSchema.Schema.Elements.Common.SimpleElement import SimpleElement

    from SimpleSchema.Schema.Elements.Types.StructureType import StructureType
    from SimpleSchema.Schema.Elements.Types.TypedefType import TypedefType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    cardinality_mock = Mock()
    metadata_mock = Mock()
    visibility_mock = Mock()
    name_mock = Mock()
    type_mock = Mock()

    tt = TypedefType(range_mock, cardinality_mock, metadata_mock, visibility_mock, name_mock, type_mock)

    assert tt.range is range_mock
    assert tt.cardinality is cardinality_mock
    assert tt.metadata is metadata_mock
    assert tt.visibility is visibility_mock
    assert tt.name is name_mock
    assert tt.type is type_mock


# ----------------------------------------------------------------------
def test_DisplayName():
    final_type = Mock()
    final_type.display_name = "Final Type"

    assert TypedefType(
        Mock(),
        Cardinality.CreateFromCode(0, 1),
        None,
        Mock(),
        SimpleElement(Mock(), "Foo"),
        final_type,
    ).display_name == "(Typedef (Foo) -> Final Type)?"

    assert TypedefType(
        Mock(),
        Cardinality.CreateFromCode(0),
        None,
        Mock(),
        SimpleElement(Mock(), "Foo"),
        TypedefType(
            Mock(),
            Cardinality.CreateFromCode(1),
            None,
            Mock(),
            SimpleElement(Mock(), "Bar"),
            final_type,
        ),
    ).display_name == "(Typedef (Foo) -> (Typedef (Bar) -> Final Type)+)*"


# ----------------------------------------------------------------------
def test_Resolve():
    single_type = StructureType(
        Mock(),
        Cardinality.CreateFromCode(),
        None,
        Mock(),
    )

    array_type = StructureType(
        Mock(),
        Cardinality.CreateFromCode(10, 10),
        None,
        Mock(),
    )

    with TypedefType(Mock(), Mock(), None, Mock(), Mock(), single_type).Resolve() as resolved_type:
        assert resolved_type is single_type

    with TypedefType(Mock(), Mock(), None, Mock(), Mock(), array_type).Resolve() as resolved_type:
        assert resolved_type is array_type


# ----------------------------------------------------------------------
def test_ResolveErrors():
    range1 = Range.Create(Path("filename1"), 3, 5, 7, 9)
    range2 = Range.Create(Path("filename2"), 1, 3, 5, 7)
    final_range = Range.Create(Path("filename3"), 5, 10, 15, 20)
    internal_range = Range.Create(Path("filename4"), 100, 200, 300, 400)

    final_type = Mock()

    # ----------------------------------------------------------------------
    @contextmanager
    def Resolve():
        try:
            yield final_type
        except SimpleSchemaException as ex:
            ex.ranges.append(final_range)
            raise

    # ----------------------------------------------------------------------

    final_type.Resolve = Resolve

    try:
        with TypedefType(
            range1,
            Mock(),
            None,
            Mock(),
            Mock(),
            TypedefType(
                range2,
                Mock(),
                None,
                Mock(),
                Mock(),
                final_type,
            ),
        ).Resolve() as resolved_type:
            assert resolved_type is final_type

            raise CardinalityInvalidMetadata.Create(internal_range)

    except SimpleSchemaException as ex:
        assert len(ex.ranges) == 4
        assert ex.ranges[0] is internal_range
        assert ex.ranges[1] is final_range
        assert ex.ranges[2] is range2
        assert ex.ranges[3] is range1

        assert str(ex) == textwrap.dedent(
            """\
            Metadata cannot be associated with single elements.

                - filename4 <Ln 100, Col 200 -> Ln 300, Col 400>
                - filename3 <Ln 5, Col 10 -> Ln 15, Col 20>
                - filename2 <Ln 1, Col 3 -> Ln 5, Col 7>
                - filename1 <Ln 3, Col 5 -> Ln 7, Col 9>
            """,
        )


# ----------------------------------------------------------------------
def test_ErrorToPython():
    with pytest.raises(
        Exception,
        match=re.escape("This method should never be called for TypedefType instances."),
    ):
        TypedefType(
            Mock(),
            Mock(),
            None,
            Mock(),
            Mock(),
            Mock(),
        ).ToPython(10)
