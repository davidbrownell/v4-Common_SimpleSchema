# ----------------------------------------------------------------------
# |
# |  Element_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 09:24:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Element.py"""

import sys

from pathlib import Path

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Impl.Common.Element import Element, Range


# ----------------------------------------------------------------------
def test_Element():
    e = Element(Range.Create(Path("abcd"), 1, 2, 3, 4))
    assert e.range == Range.Create(Path("abcd"), 1, 2, 3, 4)
