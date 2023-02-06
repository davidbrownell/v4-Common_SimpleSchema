# ----------------------------------------------------------------------
# |
# |  NumberType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-28 15:54:29
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for NumberType.py"""

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
    from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.NumberType import NumberType


# ----------------------------------------------------------------------
@pytest.mark.parametrize("bits", [None, NumberType.BitsEnum.Value16, NumberType.BitsEnum.Value128])
def test_Standard(bits):
    range_mock = Mock()
    cardinality_mock = Mock()
    metadata_mock = Mock()

    nt = NumberType(range_mock, cardinality_mock, metadata_mock, bits=bits)

    assert nt.NAME == "Number"
    assert nt.SUPPORTED_PYTHON_TYPES == (float, int, )

    assert nt.range is range_mock
    assert nt.cardinality is cardinality_mock
    assert nt.metadata is metadata_mock

    assert nt.min is None
    assert nt.max is None
    assert nt.bits is bits


# ----------------------------------------------------------------------
def test_ErrorConstruct():
    with pytest.raises(
        ValueError,
        match=re.escape("100.0 > 1.0"),
    ):
        NumberType(Mock(), Mock(), None, 100.0, 1.0)


# ----------------------------------------------------------------------
def test_DisplayName():
    single = Cardinality.CreateFromCode()

    assert NumberType(Mock(), single, None).display_name == "Number"
    assert NumberType(Mock(), single, None, 10.0).display_name == "Number (>= 10.0)"
    assert NumberType(Mock(), single, None, max=20.0).display_name == "Number (<= 20.0)"
    assert NumberType(Mock(), single, None, 10.0, 20.0).display_name == "Number (>= 10.0, <= 20.0)"


# ----------------------------------------------------------------------
def test_ToPython():
    single = Cardinality.CreateFromCode()

    assert NumberType(Mock(), single, None).ToPython(5.0) == 5.0
    assert NumberType(Mock(), single, None).ToPython(5) == 5.0

    assert NumberType(Mock(), single, None, min=5.0).ToPython(5.0) == 5.0
    assert NumberType(Mock(), single, None, max=5.0).ToPython(5.0) == 5.0

    with pytest.raises(
        Exception,
        match=re.escape("'5.0' is less than '10.0'."),
    ):
        NumberType(Mock(), single, None, min=10.0).ToPython(5.0)

    with pytest.raises(
        Exception,
        match=re.escape("'5.0' is greater than '1.0'."),
    ):
        NumberType(Mock(), single, None, max=1.0).ToPython(5.0)
