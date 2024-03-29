# ----------------------------------------------------------------------
# |
# |  BooleanType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-28 14:54:49
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for BooleanType.py"""

import re
import sys

from pathlib import Path
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.BooleanType import BooleanType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()

    bt = BooleanType(range_mock)

    assert bt.NAME == "Boolean"
    assert bt.SUPPORTED_PYTHON_TYPES == (bool, )

    assert bt.range is range_mock


# ----------------------------------------------------------------------
def test_DisplayType():
    assert BooleanType(Mock()).display_type == "Boolean"


# ----------------------------------------------------------------------
def test_ToPython():
    bt = BooleanType(Mock())

    assert bt.ToPython(True) is True
    assert bt.ToPython(False) is False
