# ----------------------------------------------------------------------
# |
# |  SimpleSchemaException_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 09:37:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for SimpleSchemaException.py"""

import sys

from pathlib import Path

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException, Range


# ----------------------------------------------------------------------
def test_Standard():
    r = SimpleSchemaException("This is the message", Range.Create(Path("the filename"), 1, 2, 3, 4))

    assert str(r) == "This is the message (the filename <[1, 2] -> [3, 4]>)"
    assert r.range == Range.Create(Path("the filename"), 1, 2, 3, 4)
