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
    from SimpleSchema.Schema.Elements.Types.StructureType import StructureType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    statement_mock = Mock()

    s = StructureType(range_mock, statement_mock)

    assert s.range is range_mock
    assert s.structure is statement_mock


# ----------------------------------------------------------------------
def test_DisplayType():
    statement_mock = Mock()
    statement_mock.name.value = "Mocked Statement"

    assert StructureType(Mock(), statement_mock).display_type == "Mocked Statement"


# ----------------------------------------------------------------------
def test_ErrorToPython():
    with pytest.raises(
        Exception,
        match=re.escape("This method should never be called for StructureType instances."),
    ):
        StructureType(Mock(), Mock()).ToPython("test")
