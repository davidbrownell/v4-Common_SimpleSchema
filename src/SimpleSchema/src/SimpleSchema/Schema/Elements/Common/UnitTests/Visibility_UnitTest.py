# ----------------------------------------------------------------------
# |
# |  Visibility_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 08:53:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Visibility.py"""

import sys

from pathlib import Path
from unittest.mock import MagicMock as Mock

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Visibility import *


# ----------------------------------------------------------------------
def test_Standard():
    assert True


# ----------------------------------------------------------------------
def test_VisibilityTraits():
    visibility_mock = Mock()

    vt = VisibilityTrait(visibility_mock)

    assert vt.visibility is visibility_mock
