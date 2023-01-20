# ----------------------------------------------------------------------
# |
# |  BooleanExpression_UnitTest.py
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
"""Unit tests for BooleanExpression.py"""

import sys

from pathlib import Path
from unittest.mock import MagicMock as Mock

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Expressions.BooleanExpression import BooleanExpression


# ----------------------------------------------------------------------
def test_Standard():
    range_value = Mock()

    i = BooleanExpression(range_value, True)

    assert i.range is range_value
    assert i.NAME == "Boolean"
    assert i.value == True
