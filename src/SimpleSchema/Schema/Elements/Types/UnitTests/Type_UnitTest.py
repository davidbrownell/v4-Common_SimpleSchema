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
from typing import ClassVar, Optional
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Types import overridemethod


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Types.Type import Cardinality, Metadata, Range, Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MyType(Type):
    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                     = "MyType"

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
    assert MyType(Mock(), Mock(), None).display_name == "MyType"


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
def test_Error():
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class MyBadType(Type):
        # ----------------------------------------------------------------------
        @overridemethod
        def _CloneImpl(self, *args, **kwargs):
            raise Exception("Never Called")

    # ----------------------------------------------------------------------

    with pytest.raises(
        AssertionError,
        match=re.escape("Make sure to define the type's name."),
    ):
        MyBadType(Mock(), Mock(), None)
