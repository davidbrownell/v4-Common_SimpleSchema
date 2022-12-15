# ----------------------------------------------------------------------
# |
# |  NoneExpression_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 10:38:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for NoneExpression.py"""

import sys

from pathlib import Path

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Impl.Common.Range import Range
    from SimpleSchema.Schema.Impl.Expressions.NoneExpression import NoneExpression


# ----------------------------------------------------------------------
def test_Standard():
    n = NoneExpression(Range.Create(Path("none_file"), 1, 2, 3, 4))

    assert n.range == Range.Create(Path("none_file"), 1, 2, 3, 4)
