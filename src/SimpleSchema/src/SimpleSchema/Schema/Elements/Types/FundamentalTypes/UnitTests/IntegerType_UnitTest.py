# ----------------------------------------------------------------------
# |
# |  IntegerType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-28 15:45:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for IntegerType.py"""

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
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.IntegerType import IntegerType


# ----------------------------------------------------------------------
@pytest.mark.parametrize("bits", [None, IntegerType.BitsEnum.Value8, IntegerType.BitsEnum.Value128])
def test_Standard(bits):
    range_mock = Mock()

    it = IntegerType(range_mock, bits=bits)

    assert it.NAME == "Integer"
    assert it.SUPPORTED_PYTHON_TYPES == (int, )

    assert it.range is range_mock

    assert it.min is None
    assert it.max is None
    assert it.bits is bits


# ----------------------------------------------------------------------
def test_ErrorConstruct():
    with pytest.raises(
        ValueError,
        match=re.escape("100 > 1"),
    ):
        IntegerType(Mock(), 100, 1)


# ----------------------------------------------------------------------
def test_DisplayType():
    assert IntegerType(Mock()).display_type == "Integer"
    assert IntegerType(Mock(), 10).display_type == "Integer {>= 10}"
    assert IntegerType(Mock(), max=20).display_type == "Integer {<= 20}"
    assert IntegerType(Mock(), 10, 20).display_type == "Integer {>= 10, <= 20}"


# ----------------------------------------------------------------------
def test_ToPython():
    assert IntegerType(Mock()).ToPython(5) == 5
    assert IntegerType(Mock(), min=5).ToPython(5) == 5
    assert IntegerType(Mock(), max=5).ToPython(5) == 5

    with pytest.raises(
        Exception,
        match=re.escape("'5' is less than '10'."),
    ):
        IntegerType(Mock(), min=10).ToPython(5)

    with pytest.raises(
        Exception,
        match=re.escape("'5' is greater than '1'."),
    ):
        IntegerType(Mock(), max=1).ToPython(5)
