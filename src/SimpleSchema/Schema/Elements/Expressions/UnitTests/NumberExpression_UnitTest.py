# ----------------------------------------------------------------------
# |
# |  NumberExpression_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 12:29:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for NumberExpression.py"""

import sys

from pathlib import Path
from unittest.mock import MagicMock as Mock

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Expressions.NumberExpression import NumberExpression


# ----------------------------------------------------------------------
def test_Standard():
    range_value = Mock()

    i = NumberExpression(range_value, 1234.5)

    assert i.range is range_value
    assert i.NAME == "Number"
    assert i.value == 1234.5
