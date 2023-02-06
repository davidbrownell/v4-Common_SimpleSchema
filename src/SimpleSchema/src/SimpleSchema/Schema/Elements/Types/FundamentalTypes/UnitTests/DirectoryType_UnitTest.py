# ----------------------------------------------------------------------
# |
# |  DirectoryType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-28 15:04:22
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for DirectoryType.py"""

import re
import sys

from pathlib import Path
from unittest.mock import MagicMock as Mock
from uuid import uuid4

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.DirectoryType import DirectoryType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    cardinality = Cardinality.CreateFromCode()
    metadata_mock = Mock()

    dt = DirectoryType(range_mock, cardinality, metadata_mock)

    assert dt.NAME == "Directory"
    assert dt.SUPPORTED_PYTHON_TYPES == (Path, )

    assert dt.range is range_mock
    assert dt.cardinality is cardinality
    assert dt.metadata is metadata_mock

    assert dt.ensure_exists is True


# ----------------------------------------------------------------------
def test_DisplayName():
    assert DirectoryType(Mock(), Cardinality.CreateFromCode(), None, ensure_exists=True).display_name == "Directory!"
    assert DirectoryType(Mock(), Cardinality.CreateFromCode(), None, ensure_exists=False).display_name == "Directory"


# ----------------------------------------------------------------------
def test_ToPython():
    value = Path.cwd()

    assert DirectoryType(Mock(), Cardinality.CreateFromCode(), None).ToPython(value) == value

    does_not_exist = value / str(uuid4())

    assert not does_not_exist.is_dir()

    assert DirectoryType(Mock(), Cardinality.CreateFromCode(), None, ensure_exists=False).ToPython(value) == value

    with pytest.raises(
        Exception,
        match=re.escape("'{}' is not a valid directory.".format(does_not_exist)),
    ):
        DirectoryType(Mock(), Cardinality.CreateFromCode(), None).ToPython(does_not_exist)
