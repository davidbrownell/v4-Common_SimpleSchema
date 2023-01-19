# ----------------------------------------------------------------------
# |
# |  ItemStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-04 13:18:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ItemStatement.py"""

import sys

from pathlib import Path
from unittest import mock

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Statements.ItemStatement import ItemStatement


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = mock.MagicMock()
    name_mock = mock.MagicMock()
    type_mock = mock.MagicMock()

    s = ItemStatement(range_mock, name_mock, type_mock)

    assert s.range is range_mock
    assert s.name is name_mock
    assert s.type is type_mock
