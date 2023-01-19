# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-03 11:15:54
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Implements common test functionality"""

import sys

from dataclasses import dataclass
from pathlib import Path

import rtyaml

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.TestHelpers.StreamTestHelpers import GenerateDoneManagerAndSink


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Parse.ANTLR import *  # pylint: disable=unused-wildcard-import,wildcard-import
    from SimpleSchema.Schema.Parse import TestHelpersImpl


# Convenience Imports
from SimpleSchema.Schema.Parse.TestHelpersImpl import CompareResultsFromFile, ScrubString, DEFAULT_WORKSPACE_PATH  # pylint: disable=unused-import,wrong-import-position


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MultipleReturnValue(object):
    dict_results: Dict[str, Union[Exception, List[Dict[str, Any]]]]
    output: str


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def Test(
    content: str,
    *,
    single_threaded: bool=False,
    quiet: bool=False,
    raise_if_single_exception: bool=True,
) -> Tuple[str, str]:
    result = TestMultiple(
        {
            "root_file": content,
        },
        ["root_file", ],
        single_threaded=single_threaded,
        quiet=quiet,
        raise_if_single_exception=raise_if_single_exception,
    )

    assert len(result.dict_results) == 1
    assert "root_file" in result.dict_results

    yaml_result = TestHelpersImpl.ScrubString(rtyaml.dump(result.dict_results["root_file"]))

    return yaml_result, result.output


# ----------------------------------------------------------------------
def TestMultiple(
    all_content: Dict[str, str],
    initial_filenames: List[str],
    *,
    single_threaded: bool=False,
    quiet: bool=False,
    raise_if_single_exception: bool=True,
) -> MultipleReturnValue:
    with TestHelpersImpl.GenerateMockedPath(all_content, initial_filenames) as workspaces:
        dm_and_sink = iter(GenerateDoneManagerAndSink())

        parse_results = Parse(
            cast(DoneManager, next(dm_and_sink)),
            workspaces,
            single_threaded=single_threaded,
            quiet=quiet,
            raise_if_single_exception=raise_if_single_exception,
        )

        output = cast(str, next(dm_and_sink))

    assert len(parse_results) == 1, parse_results
    assert TestHelpersImpl.DEFAULT_WORKSPACE_PATH in parse_results

    parse_results = parse_results[TestHelpersImpl.DEFAULT_WORKSPACE_PATH]

    return MultipleReturnValue(
        {
            filename.as_posix(): TestHelpersImpl.ToDict(parse_result) if isinstance(parse_result, RootStatement) else parse_result
            for filename, parse_result in parse_results.items()
        },
        output,
    )
