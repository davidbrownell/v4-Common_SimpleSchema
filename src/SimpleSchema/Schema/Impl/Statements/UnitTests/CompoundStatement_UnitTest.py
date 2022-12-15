# ----------------------------------------------------------------------
# |
# |  CompoundStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 11:12:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for CompoundStatement.py"""

import sys

from pathlib import Path
from unittest import mock

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Impl.Statements.CompoundStatement import CompoundStatement


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = mock.MagicMock()
    name_mock = mock.MagicMock()

    s = CompoundStatement(range_mock, name_mock, None, None, [])

    assert s.range is range_mock
    assert s.name is name_mock
    assert s.base is None
    assert s.metadata is None
    assert s.statements == []

    base_mock = mock.MagicMock()
    metadata_mock = mock.MagicMock()
    statement1_mock = mock.MagicMock()
    statement2_mock = mock.MagicMock()

    s = CompoundStatement(range_mock, name_mock, base_mock, metadata_mock, [statement1_mock, statement2_mock])

    assert s.range is range_mock
    assert s.name is name_mock
    assert s.base is base_mock
    assert s.metadata is metadata_mock
    assert s.statements == [statement1_mock, statement2_mock]
