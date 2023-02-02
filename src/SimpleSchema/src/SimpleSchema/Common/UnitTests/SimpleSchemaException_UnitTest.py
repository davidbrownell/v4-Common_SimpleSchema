# ----------------------------------------------------------------------
# |
# |  SimpleSchemaException_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 20:26:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for SimpleSchemaException.py"""

import sys
import textwrap

from pathlib import Path

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Common.SimpleSchemaException import DynamicSimpleSchemaException, Range, SimpleSchemaException


# ----------------------------------------------------------------------
Exception1              = DynamicSimpleSchemaException.CreateType("a: {a}; b: {b}; c: {c}", a=int, b=bool, c=str)
Exception2              = DynamicSimpleSchemaException.CreateType(
    textwrap.dedent(
        """\
        a: {a}
        b: {b}
        c: {c}
        """,
    ),
    a=int, b=bool, c=str,
)


# ----------------------------------------------------------------------
def test_Exception1():
    ex = Exception1.Create(Range.Create(Path("file"), 1, 2, 3, 4), 10, True, "string")

    assert isinstance(ex, Exception1)
    assert not isinstance(ex, Exception2)

    assert str(ex) == "a: 10; b: True; c: string (file <Ln 1, Col 2 -> Ln 3, Col 4>)"

    ex = Exception1.Create(
        [Range.Create(Path("file1"), 1, 2, 3, 4), Range.Create(Path("file2"), 10, 20, 30, 40), ],
        100,
        False,
        "string",
    )

    assert isinstance(ex, Exception1)
    assert str(ex) == textwrap.dedent(
        """\
        a: 100; b: False; c: string

            - file1 <Ln 1, Col 2 -> Ln 3, Col 4>
            - file2 <Ln 10, Col 20 -> Ln 30, Col 40>
        """,
    )


# ----------------------------------------------------------------------
def test_Exception2():
    ex = Exception2.Create(
        Range.Create(Path("file"), 1, 2, 3, 4),
        10,
        True,
        "string",
    )

    assert isinstance(ex, Exception2)
    assert not isinstance(ex, Exception1)

    assert str(ex) == textwrap.dedent(
        """\
        a: 10
        b: True
        c: string

            - file <Ln 1, Col 2 -> Ln 3, Col 4>
        """,
    )

    ex = Exception2.Create(
        [Range.Create(Path("file1"), 1, 2, 3, 4), Range.Create(Path("file2"), 10, 20, 30, 40), ],
        100,
        False,
        "string",
    )

    assert isinstance(ex, Exception2)
    assert str(ex) == textwrap.dedent(
        """\
        a: 100
        b: False
        c: string

            - file1 <Ln 1, Col 2 -> Ln 3, Col 4>
            - file2 <Ln 10, Col 20 -> Ln 30, Col 40>
        """,
    )
