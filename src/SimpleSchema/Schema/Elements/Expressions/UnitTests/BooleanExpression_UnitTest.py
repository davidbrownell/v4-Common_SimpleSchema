# ----------------------------------------------------------------------
# |
# |  BooleanExpression_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 10:34:21
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for BooleanExpression.py"""

import sys

from pathlib import Path

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Range import Range
    from SimpleSchema.Schema.Elements.Expressions.BooleanExpression import BooleanExpression


# ----------------------------------------------------------------------
def test_Standard():
    b = BooleanExpression(Range.Create(Path("true_file"), 1, 2, 3, 4), True)

    assert b.range == Range.Create(Path("true_file"), 1, 2, 3, 4)
    assert b.value is True

    b = BooleanExpression(Range.Create(Path("false_file"), 10, 20, 30, 40), False)

    assert b.range == Range.Create(Path("false_file"), 10, 20, 30, 40)
    assert b.value is False
