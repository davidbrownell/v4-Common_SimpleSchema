# ----------------------------------------------------------------------
# |
# |  SimpleElement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 08:55:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for SimpleElement.py"""

import sys

from pathlib import Path
from unittest.mock import MagicMock as Mock

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Common.SimpleElement import SimpleElement


# ----------------------------------------------------------------------
def test_String():
    range_mock = Mock()

    e = SimpleElement(range_mock, "Hello!")

    assert e.range is range_mock
    assert e.value == "Hello!"


# ----------------------------------------------------------------------
def test_Int():
    range_mock = Mock()

    e = SimpleElement(range_mock, 10)

    assert e.range is range_mock
    assert e.value == 10
