# ----------------------------------------------------------------------
# |
# |  VariantType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 11:17:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
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
    from SimpleSchema.Schema.Impl.Common.Range import Range
    from SimpleSchema.Schema.Impl.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Impl.Types.VariantType import VariantType, Type


# ----------------------------------------------------------------------
def test_Standard():
    i1 = Type(mock.MagicMock(), mock.MagicMock(), mock.MagicMock())
    i2 = Type(mock.MagicMock(), mock.MagicMock(), mock.MagicMock())

    cardinality = mock.MagicMock()
    metadata = mock.MagicMock()

    t = VariantType(
        Range.Create(Path("variant_file"), 1, 1, 3, 1),
        cardinality,
        metadata,
        [i1],
    )

    assert t.range == Range.Create(Path("variant_file"), 1, 1, 3, 1)
    assert t.cardinality is cardinality
    assert t.metadata is metadata
    assert t.types == [i1]

    t = VariantType(
        mock.MagicMock(),
        mock.MagicMock(),
        mock.MagicMock(),
        [i1, i2],
    )

    assert t.types == [i1, i2]


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
            Range.Create(Path("file"), 1, 2, 3, 4),
            mock.MagicMock(),
            mock.MagicMock(),
            [
                Type(mock.MagicMock(), mock.MagicMock(), mock.MagicMock()),
                VariantType(
                    Range.Create(Path("invalid_variant_file"), 10, 20, 30, 40),
                    mock.MagicMock(),
                    mock.MagicMock(),
                    [
                        mock.MagicMock(),
                    ],
                ),
                Type(mock.MagicMock(), mock.MagicMock(), mock.MagicMock()),
            ],
        )
