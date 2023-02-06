# ----------------------------------------------------------------------
# |
# |  UriType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-28 15:59:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for UriType.py"""

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
    from SimpleSchema.Schema.Elements.Types.FundamentalTypes.UriType import Uri, UriType


# ----------------------------------------------------------------------
class TestUriAuthority(object):
    # ----------------------------------------------------------------------
    def test_Standard(self):
        assert str(Uri.Authority("//", None, "foo.bar", None)) == "//foo.bar/"

    # ----------------------------------------------------------------------
    def test_WithUsername(self):
        assert str(Uri.Authority("////", "the_username", "foo.bar", None)) == "////the_username@foo.bar/"

    # ----------------------------------------------------------------------
    def test_WithPort(self):
        assert str(Uri.Authority("__", None, "foo.bar", 1234)) == "__foo.bar:1234/"

    # ----------------------------------------------------------------------
    def test_Complete(self):
        assert str(Uri.Authority("//", "the_username", "foo.bar", 1234)) == "//the_username@foo.bar:1234/"


# ----------------------------------------------------------------------
class TestUri(object):
    # ----------------------------------------------------------------------
    def test_Standard(self):
        assert str(Uri("file", None, "the_path", None, None)) == "file:the_path"

    # ----------------------------------------------------------------------
    def test_WithAuthority(self):
        assert str(Uri("https", Uri.Authority("//", None, "foo.bar", None), "", None, None)) == "https://foo.bar/"

    # ----------------------------------------------------------------------
    def test_WithQuery(self):
        assert str(Uri("file", None, "", "the_query", None)) == "file:?the_query"

    # ----------------------------------------------------------------------
    def test_WithFragment(self):
        assert str(Uri("file", None, "", None, "the_fragment")) == "file:#the_fragment"

    # ----------------------------------------------------------------------
    def test_Complete(self):
        assert str(Uri("https", Uri.Authority("//", None, "foo.bar", 1234), "the_path", "the_query", "the_fragment")) == "https://foo.bar:1234/the_path?the_query#the_fragment"


# ----------------------------------------------------------------------
class TestUriType(object):
    # ----------------------------------------------------------------------
    def test_Standard(self):
        range_mock = Mock()
        cardinality_mock = Mock()
        metadata_mock = Mock()

        ut = UriType(range_mock, cardinality_mock, metadata_mock)

        assert ut.NAME == "Uri"
        assert ut.SUPPORTED_PYTHON_TYPES == (str, Uri, )

        assert ut.range is range_mock
        assert ut.cardinality is cardinality_mock
        assert ut.metadata is metadata_mock

    # ----------------------------------------------------------------------
    def test_DisplayName(self):
        assert UriType(Mock(), Cardinality.CreateFromCode(), None).display_name == "Uri"

    # ----------------------------------------------------------------------
    @pytest.mark.parametrize("trailing_slash", ["", "/"])
    def test_ToPython(self, trailing_slash):
        uri_type = UriType(Mock(), Cardinality.CreateFromCode(), None)

        uri = uri_type.ToPython("https://foo.bar{}".format(trailing_slash))

        assert uri == Uri("https", Uri.Authority("//", None, "foo.bar", None), None, None, None)
        assert uri_type.ToPython(uri) is uri

        assert uri_type.ToPython("https://foo.bar/one/two/three") == Uri("https", Uri.Authority("//", None, "foo.bar", None), "one/two/three", None, None)
        assert uri_type.ToPython("https://foo.bar:1234/one/two/three") == Uri("https", Uri.Authority("//", None, "foo.bar", 1234), "one/two/three", None, None)

        with pytest.raises(
            Exception,
            match=re.escape("'this is not a valid uri' is not a valid URI."),
        ):
            uri_type.ToPython("this is not a valid uri")
