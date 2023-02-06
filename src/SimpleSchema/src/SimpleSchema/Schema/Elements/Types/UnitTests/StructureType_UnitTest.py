# ----------------------------------------------------------------------
# |
# |  StructureType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-24 12:50:54
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for StructureType.py"""

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
    from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality

    from SimpleSchema.Schema.Elements.Types.StructureType import StructureType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    cardinality_mock = Mock()
    metadata_mock = Mock()
    statement_mock = Mock()

    s = StructureType(range_mock, cardinality_mock, metadata_mock, statement_mock)

    assert s.range is range_mock
    assert s.cardinality is cardinality_mock
    assert s.metadata is metadata_mock
    assert s.statement is statement_mock


# ----------------------------------------------------------------------
def test_DisplayName():
    statement_mock = Mock()
    statement_mock.name.value = "Mocked Statement"

    assert StructureType(Mock(), Cardinality.CreateFromCode(0, 1), None, statement_mock).display_name == "Mocked Statement?"
    assert StructureType(Mock(), Cardinality.CreateFromCode(4, 4), None, statement_mock).display_name == "Mocked Statement[4]"


# ----------------------------------------------------------------------
def test_ErrorToPython():
    with pytest.raises(
        Exception,
        match=re.escape("This method should never be called for StructureType instances."),
    ):
        StructureType(Mock(), Cardinality.CreateFromCode(), None, Mock()).ToPython("test")
