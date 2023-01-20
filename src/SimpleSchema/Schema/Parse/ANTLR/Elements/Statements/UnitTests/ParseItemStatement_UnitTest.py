# ----------------------------------------------------------------------
# |
# |  ParseItemStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 10:42:13
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ParseItemStatement.py"""

import sys

from pathlib import Path
from unittest.mock import MagicMock as Mock

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseItemStatement import ParseItemStatement


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    name_mock = Mock()
    type_mock = Mock()

    s = ParseItemStatement(range_mock, name_mock, type_mock)

    assert s.range is range_mock
    assert s.name is name_mock
    assert s.type is type_mock
