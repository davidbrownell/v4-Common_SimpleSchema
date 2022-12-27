# ----------------------------------------------------------------------
# |
# |  TestHelpers.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-27 13:18:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Various test helpers"""

import sys

from pathlib import Path
from typing import cast, Set, Tuple

import pytest
import rtyaml

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Streams.DoneManager import DoneManager
from Common_Foundation.TestHelpers.StreamTestHelpers import GenerateDoneManagerAndSink

pytest.register_assert_rewrite("Common_PythonDevelopment.TestHelpers")

from Common_PythonDevelopment.TestHelpers import CompareResultsFromFile as CompareResultsFromFileImpl


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement
    from SimpleSchema.Schema.Parse import Parse
    from SimpleSchema.Schema.Lower import *


# ----------------------------------------------------------------------
def CompareResultsFromFile(
    content: str,
    call_stack_offset: int=0,
    suffix: Optional[str]=None,
) -> None:
    CompareResultsFromFileImpl(
        content,
        file_extension=".yaml",
        call_stack_offset=call_stack_offset + 1,
        decorate_test_name_func=lambda value: value[len("test_"):],
        decorate_stem_func=lambda value: value[:-len("_IntegrationTest")],
        suffix=suffix,
    )


# ----------------------------------------------------------------------
def Test(
    content: str,
    *,
    single_threaded: bool=False,
    quiet: bool=False,
    raise_if_single_exception: bool=True,
) -> Tuple[RootStatement, str]:

    dm_and_sink = iter(GenerateDoneManagerAndSink())

    parse_results = Parse(
        cast(DoneManager, next(dm_and_sink)),
        {
            Path("workspace"): {
                Path("root_file"): lambda: content,
            },
        },
        single_threaded=single_threaded,
        quiet=quiet,
        raise_if_single_exception=raise_if_single_exception,
    )

    output = cast(str, next(dm_and_sink))

    assert len(parse_results) == 1, parse_results
    parse_results = next(iter(parse_results.values()))

    assert len(parse_results) == 1, parse_results
    parse_results = next(iter(parse_results.values()))

    assert isinstance(parse_results, RootStatement), parse_results

    parse_results = Lower(parse_results)

    return parse_results, output
