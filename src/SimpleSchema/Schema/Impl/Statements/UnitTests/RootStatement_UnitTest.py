# ----------------------------------------------------------------------
# |
# |  RootStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 11:14:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for RootStatement.py"""

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

    from SimpleSchema.Schema.Impl.Statements.DataMemberStatement import DataMemberStatement, IdentifierExpression
    from SimpleSchema.Schema.Impl.Statements.RootStatement import RootStatement

    from SimpleSchema.Schema.Impl.Types.IdentifierType import IdentifierType


# ----------------------------------------------------------------------
def test_Empty():
    r = RootStatement(Range.Create(Path("root_file"), 1, 2, 3, 4), [])

    assert r.range == Range.Create(Path("root_file"), 1, 2, 3, 4)
    assert r.statements == []


# ----------------------------------------------------------------------
def test_WithStatements():
    s1 = DataMemberStatement(
        Range.Create(Path("data_file"), 10, 20, 30, 40),
        IdentifierExpression(Range.Create(Path("id_file"), 1, 2, 3, 4), "foo"),
        IdentifierType(Range.Create(Path("type_file"), 1, 2, 3, 4), "Bar"),
        None,
    )

    r = RootStatement(Range.Create(Path("root_file"), 1, 2, 3, 4), [s1, s1])

    assert r.range == Range.Create(Path("root_file"), 1, 2, 3, 4)
    assert r.statements == [s1, s1]


# ----------------------------------------------------------------------
def test_ErrorNestedRoot():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("Root statements may not contain nested root statements. (invalid_root <[10, 20] -> [30, 40]>)"),
    ):
        RootStatement(
            Range.Create(Path("root"), 1, 2, 3, 4),
            [
                RootStatement(Range.Create(Path("invalid_root"), 10, 20, 30, 40), []),
            ],
        )
