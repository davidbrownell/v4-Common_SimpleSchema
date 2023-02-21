# ----------------------------------------------------------------------
# |
# |  StructureStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 10:29:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for StructureStatement.py"""

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

    from SimpleSchema.Schema.Elements.Statements.StructureStatement import StructureStatement
    from SimpleSchema.Schema.Elements.Types.TupleType import TupleType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    visibility_mock = Mock()
    name_mock = Mock()

    ss = StructureStatement(range_mock, visibility_mock, name_mock, [], [])

    assert ss.range is range_mock
    assert ss.visibility is visibility_mock
    assert ss.name is name_mock
    assert ss.base_types == []
    assert ss.children == []
