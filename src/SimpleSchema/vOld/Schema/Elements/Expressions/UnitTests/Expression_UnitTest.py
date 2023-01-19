# ----------------------------------------------------------------------
# |
# |  Expression_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 10:35:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Expression.py"""

import sys

from dataclasses import dataclass
from pathlib import Path

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Range import Range
    from SimpleSchema.Schema.Elements.Expressions.Expression import Expression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MyExpression(Expression):
    NAME = "MyExpression"


# ----------------------------------------------------------------------
def test_Standard():
    e = MyExpression(Range.Create(Path("the_file"), 1, 2, 3, 4))

    assert e.NAME == "MyExpression"
    assert e.range == Range.Create(Path("the_file"), 1, 2, 3, 4)
