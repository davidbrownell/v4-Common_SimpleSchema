# ----------------------------------------------------------------------
# |
# |  IntegerExpression_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 10:53:20
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for IntegerExpression.py"""

import sys

from pathlib import Path
from unittest.mock import MagicMock as Mock

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression


# ----------------------------------------------------------------------
def test_Standard():
    range_value = Mock()

    i = IntegerExpression(range_value, 1234)

    assert i.range is range_value
    assert i.NAME == "Integer"
    assert i.value == 1234
