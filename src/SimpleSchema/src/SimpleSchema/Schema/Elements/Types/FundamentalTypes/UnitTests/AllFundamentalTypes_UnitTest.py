# ----------------------------------------------------------------------
# |
# |  AllFundamentalTypes_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-28 16:36:25
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for AllFundamentalTypes.py"""

import sys

from pathlib import Path

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes import AllFundamentalTypes  # pylint: disable=unused-import


# ----------------------------------------------------------------------
def test_Standard():
    # Nothing to test as it is just importing content
    assert True
