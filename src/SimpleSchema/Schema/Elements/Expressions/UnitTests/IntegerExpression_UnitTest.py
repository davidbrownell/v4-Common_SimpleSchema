# ----------------------------------------------------------------------
# |
# |  IntegerExpression_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 10:36:47
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for IntegerExpression.py"""

import sys

from pathlib import Path

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Range import Range
    from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression


# ----------------------------------------------------------------------
def test_Standard():
    i = IntegerExpression(Range.Create(Path("integer_file"), 1, 2, 3, 4), 100)

    assert i.range == Range.Create(Path("integer_file"), 1, 2, 3, 4)
    assert i.value == 100
