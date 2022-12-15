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

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Impl.Common.Range import Range
    from SimpleSchema.Schema.Impl.Common.SimpleSchemaException import SimpleSchemaException

    from SimpleSchema.Schema.Impl.Types.VariantType import VariantType, IdentifierType


# ----------------------------------------------------------------------
def test_Standard():
    i1 = IdentifierType(Range.Create(Path("variant_file"), 1, 1, 2, 1), "ID1")
    i2 = IdentifierType(Range.Create(Path("variant_file"), 2, 1, 3, 1), "ID2")

    t = VariantType(Range.Create(Path("variant_file"), 1, 1, 3, 1), [i1])

    assert t.range == Range.Create(Path("variant_file"), 1, 1, 3, 1)
    assert t.types == [i1]

    t = VariantType(Range.Create(Path("variant_file"), 1, 1, 3, 1), [i1, i2])
    assert t.types == [i1, i2]


# ----------------------------------------------------------------------
def test_ErrorEmpty():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("No types were provided. (file <[1, 2] -> [3, 4]>)"),
    ):
        VariantType(Range.Create(Path("file"), 1, 2, 3, 4), [])


# ----------------------------------------------------------------------
def test_ErrorInvalidTypes():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Nested variant types must be identifier types. (invalid_variant_file <[10, 20] -> [30, 40]>)"),
    ):
        VariantType(
            Range.Create(Path("file"), 1, 2, 3, 4),
            [
                IdentifierType(Range.Create(Path("id_file"), 1, 2, 3, 4), "ID1"),
                VariantType(
                    Range.Create(Path("invalid_variant_file"), 10, 20, 30, 40),
                    [
                        IdentifierType(Range.Create(Path("id_file"), 1, 2, 3, 4), "ID2"),
                    ],
                ),
                IdentifierType(Range.Create(Path("id_file"), 1, 2, 3, 4), "ID3"),
            ],
        )
