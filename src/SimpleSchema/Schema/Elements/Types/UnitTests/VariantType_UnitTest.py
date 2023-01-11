# ----------------------------------------------------------------------
# |
# |  VariantType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-04 14:23:42
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for VariantType.py"""

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
    from SimpleSchema.Schema.Elements.Types.VariantType import VariantType, SimpleSchemaException


# ----------------------------------------------------------------------
def test_Standard():
    range_mock = mock.MagicMock()
    cardinality = mock.MagicMock()
    metadata = mock.MagicMock()
    i1_mock = mock.MagicMock()
    i2_mock = mock.MagicMock()

    t = VariantType(
        range_mock,
        cardinality,
        metadata,
        [i1_mock],
    )

    assert t.range is range_mock
    assert t.cardinality is cardinality
    assert t.metadata is metadata
    assert t.types == [i1_mock]

    t = VariantType(
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
        VariantType(
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
        VariantType(
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            [
                mock.MagicMock(),
                VariantType(
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
