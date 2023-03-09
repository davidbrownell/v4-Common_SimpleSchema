# ----------------------------------------------------------------------
# |
# |  ExecuteInParallel_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-03-08 14:27:43
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for ExecuteInParallel.py."""

import re
import sys
import textwrap

from pathlib import Path
from typing import cast
from unittest.mock import MagicMock as Mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Streams.DoneManager import DoneManager
from Common_Foundation.TestHelpers.StreamTestHelpers import GenerateDoneManagerAndSink

from Common_FoundationEx import ExecuteTasks


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Common.ExecuteInParallel import ExecuteInParallel


# ----------------------------------------------------------------------
def test_Standard():
    # ----------------------------------------------------------------------
    def Execute(
        x: int,
        status: ExecuteTasks.Status,
    ) -> int:
        status.OnInfo("Before")

        x *= 2

        status.OnInfo("After")

        return x

    # ----------------------------------------------------------------------

    dm_and_sink = GenerateDoneManagerAndSink()

    results = ExecuteInParallel(
        cast(DoneManager, next(dm_and_sink)),
        "Standard",
        {
            Path(str(x)): x
            for x in range(10)
        },
        Execute,
        quiet=False,
        max_num_threads=None,
        raise_if_single_exception=False,
    )

    assert results == {
        Path(str(x)): x * 2
        for x in range(10)
    }

    output = cast(str, next(dm_and_sink))

    assert output == textwrap.dedent(
        """\
        Heading...
          Standard (10 items)...DONE! (0, <scrubbed duration>, 10 items succeeded, no items with errors, no items with warnings)
        DONE! (0, <scrubbed duration>)
        """,
    )


# ----------------------------------------------------------------------
@pytest.mark.parametrize("raise_if_single_exception", [False, True])
def test_Exceptions(
    raise_if_single_exception: bool,
):
    # ----------------------------------------------------------------------
    def Execute(
        x: int,
        status: ExecuteTasks.Status,
    ) -> int:
        if x & 1:
            raise Exception("Odd numbers are not supported")

        return x * 2

    # ----------------------------------------------------------------------

    dm_and_sink = GenerateDoneManagerAndSink()

    results = ExecuteInParallel(
        cast(DoneManager, next(dm_and_sink)),
        "Exceptions",
        {
            Path(str(x)): x
            for x in range(10)
        },
        Execute,
        quiet=False,
        max_num_threads=None,
        raise_if_single_exception=raise_if_single_exception,  # This value should not impact the result as multiple exceptions are raised
    )

    assert {
        key.name: str(value)
        for key, value in results.items()
    } == {
        str(x): "Odd numbers are not supported"
        for x in range(1, 10, 2)
    }


# ----------------------------------------------------------------------
@pytest.mark.parametrize("raise_if_single_exception", [False, True])
def test_SingleException(
    raise_if_single_exception: bool,
):
    # ----------------------------------------------------------------------
    def Execute(
        x: int,
        status: ExecuteTasks.Status,
    ) -> int:
        if x == 6:
            raise Exception("Exception on 6")

        return x * 2

    # ----------------------------------------------------------------------

    dm_and_sink = GenerateDoneManagerAndSink()

    items: dict[Path, int] = {
        Path(str(x)): x
        for x in range(10)
    }

    if raise_if_single_exception:
        with pytest.raises(
            Exception,
            match=re.escape("Exception on 6"),
        ):
            ExecuteInParallel(
                cast(DoneManager, next(dm_and_sink)),
                "SingleException",
                items,
                Execute,
                quiet=False,
                max_num_threads=None,
                raise_if_single_exception=raise_if_single_exception,
            )
    else:
        results = ExecuteInParallel(
            cast(DoneManager, next(dm_and_sink)),
            "SingleException",
            items,
            Execute,
            quiet=False,
            max_num_threads=None,
            raise_if_single_exception=raise_if_single_exception,
        )

        assert {
            key.name: str(value)
            for key, value in results.items()
        } == {
            "6": "Exception on 6",
        }
