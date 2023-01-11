# ----------------------------------------------------------------------
# |
# |  ParseVariantType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 11:17:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ParseVariantType.py"""

import re
import sys

from pathlib import Path
from unittest import mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Range import Range
    from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseVariantType import ParseVariantType, ParseType


# ----------------------------------------------------------------------
def test_Standard():
    cardinality = mock.MagicMock()
    metadata = mock.MagicMock()
    i1_mock = mock.MagicMock()
    i2_mock = mock.MagicMock()

    t = ParseVariantType(
        Range.Create(Path("variant_file"), 1, 1, 3, 1),
        cardinality,
        metadata,
        [i1_mock],
    )

    assert t.range == Range.Create(Path("variant_file"), 1, 1, 3, 1)
    assert t.cardinality is cardinality
    assert t.metadata is metadata
    assert t.types == [i1_mock]

    t = ParseVariantType(
        mock.MagicMock(),
        mock.MagicMock(),
        mock.MagicMock(),
        [i1_mock, i2_mock],
    )

    assert t.types == [i1_mock, i2_mock]


# ----------------------------------------------------------------------
def test_ErrorEmpty():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("No types were provided. (file <[1, 2] -> [3, 4]>)"),
    ):
        ParseVariantType(
            Range.Create(Path("file"), 1, 2, 3, 4),
            mock.MagicMock(),
            mock.MagicMock(),
            [],
        )


# ----------------------------------------------------------------------
def test_ErrorInvalidTypes():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Nested variant types are not supported. (invalid_variant_file <[10, 20] -> [30, 40]>)"),
    ):
        ParseVariantType(
            Range.Create(Path("file"), 1, 2, 3, 4),
            mock.MagicMock(),
            mock.MagicMock(),
            [
                mock.MagicMock(),
                ParseVariantType(
                    Range.Create(Path("invalid_variant_file"), 10, 20, 30, 40),
                    mock.MagicMock(),
                    mock.MagicMock(),
                    [
                        mock.MagicMock(),
                    ],
                ),
                mock.MagicMock(),
            ],
        )
