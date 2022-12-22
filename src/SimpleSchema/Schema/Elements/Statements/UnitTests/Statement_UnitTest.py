# ----------------------------------------------------------------------
# |
# |  Statement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 11:15:08
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for Statement.py"""

import sys

from pathlib import Path

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Range import Range
    from SimpleSchema.Schema.Elements.Statements.Statement import Statement


# ----------------------------------------------------------------------
def test_Standard():
    s = Statement(Range.Create(Path("statement_file"), 1, 2, 3, 4))

    assert s.range == Range.Create(Path("statement_file"), 1, 2, 3, 4)
