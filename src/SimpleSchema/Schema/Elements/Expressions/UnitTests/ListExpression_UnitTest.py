# ----------------------------------------------------------------------
# |
# |  ListExpression_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-19 12:03:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ListExpression.py"""

import sys

from pathlib import Path
from unittest import mock

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Expressions.ListExpression import ListExpression


# ----------------------------------------------------------------------
def test_Construct():
    range1 = mock.MagicMock()
    range2 = mock.MagicMock()

    le = ListExpression(range1, [])

    assert le.range is range1
    assert le.items == []

    le2 = ListExpression(range1, [le, le])

    assert le2.range is range1
    assert le2.items == [le, le]
