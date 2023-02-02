# ----------------------------------------------------------------------
# |
# |  FilenameType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-28 15:28:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for FilenameType.py"""

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
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.FilenameType import FilenameType


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = Mock()
    cardinality_mock = Mock()
    metadata_mock = Mock()

    ft = FilenameType(range_mock, cardinality_mock, metadata_mock)

    assert ft.NAME == "Filename"
    assert ft.SUPPORTED_PYTHON_TYPES == (Path, )

    assert ft.range is range_mock
    assert ft.cardinality is cardinality_mock
    assert ft.metadata is metadata_mock

    assert ft.ensure_exists is True
    assert ft.match_any is False


# ----------------------------------------------------------------------
def test_DisplayName():
    single = Cardinality.CreateFromCode()

    assert FilenameType(Mock(), single, None, ensure_exists=True, match_any=True).display_name == "Filename!^"
    assert FilenameType(Mock(), single, None, ensure_exists=True, match_any=False).display_name == "Filename!"
    assert FilenameType(Mock(), single, None, ensure_exists=False, match_any=False).display_name == "Filename"


# ----------------------------------------------------------------------
def test_Clone():
    ft = FilenameType(Mock(), Mock(), Mock(), ensure_exists=False)

    assert ft.Clone() == ft


# ----------------------------------------------------------------------
class TestToPython(object):
    valid_filename                          = Path(__file__)
    valid_dir                               = valid_filename.parent

    invalid_filename                        = valid_dir / str(uuid4())

    assert not invalid_filename.exists()

    # ----------------------------------------------------------------------
    def test_TrueFalse(self):
        filename_type = FilenameType(Mock(), Mock(), Mock(), ensure_exists=True, match_any=False)

        assert filename_type.ToPython(self.valid_filename) == self.valid_filename

        with pytest.raises(
            Exception,
            match=re.escape("'{}' is not a valid filename.".format(self.invalid_filename)),
        ):
            filename_type.ToPython(self.invalid_filename)

        with pytest.raises(
            Exception,
            match=re.escape("'{}' is not a valid filename.".format(self.valid_dir)),
        ):
            filename_type.ToPython(self.valid_dir)

    # ----------------------------------------------------------------------
    def test_TrueTrue(self):
        filename_type = FilenameType(Mock(), Mock(), Mock(), ensure_exists=True, match_any=True)

        assert filename_type.ToPython(self.valid_filename) == self.valid_filename

        with pytest.raises(
            Exception,
            match=re.escape("'{}' is not a valid filename or directory.".format(self.invalid_filename)),
        ):
            filename_type.ToPython(self.invalid_filename)

        assert filename_type.ToPython(self.valid_dir) == self.valid_dir

    # ----------------------------------------------------------------------
    def test_FalseTrue(self):
        with pytest.raises(
            ValueError,
            match=re.escape("'match_any' should only be set when 'ensure_exists' is set as well."),
        ):
            FilenameType(Mock(), Mock(), None, ensure_exists=False, match_any=True)

    # ----------------------------------------------------------------------
    def test_FalseFalse(self):
        filename_type = FilenameType(Mock(), Mock(), Mock(), ensure_exists=False, match_any=False)

        assert filename_type.ToPython(self.valid_filename) == self.valid_filename
        assert filename_type.ToPython(self.invalid_filename) == self.invalid_filename
        assert filename_type.ToPython(self.valid_dir) == self.valid_dir
