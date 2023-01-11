# ----------------------------------------------------------------------
# |
# |  ParseItemStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-19 12:43:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ParseItemStatement.py"""

import sys

from pathlib import Path
from unittest import mock

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseItemStatement import ParseItemStatement


# ----------------------------------------------------------------------
def test_Standard():
    range1 = mock.MagicMock()
    name_mock = mock.MagicMock()
    type_mock = mock.MagicMock()

    data = ParseItemStatement(range1, name_mock, type_mock)

    assert data.range is range1
    assert data.name is name_mock
    assert data.type is type_mock
