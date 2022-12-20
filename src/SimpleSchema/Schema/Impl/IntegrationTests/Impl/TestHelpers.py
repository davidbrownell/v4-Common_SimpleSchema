# ----------------------------------------------------------------------
# |
# |  TestHelpers.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-19 11:54:38
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

import pytest
import rtyaml

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.TestHelpers.StreamTestHelpers import GenerateDoneManagerAndSink

pytest.register_assert_rewrite("Common_PythonDevelopment.TestHelpers")

from Common_PythonDevelopment.TestHelpers import CompareResultsFromFile as CompareResultsFromFileImpl


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Impl.Parse import *
    from SimpleSchema.Schema.Impl.Visitors.ToPythonDictVisitor import ToPythonDictVisitor


# ----------------------------------------------------------------------
def CompareResultsFromFile(
    content: str,
) -> None:
    CompareResultsFromFileImpl(
        content,
        file_extension=".yaml",
        call_stack_offset=1,
        decorate_test_name_func=lambda value: value[len("test_"):],
        decorate_stem_func=lambda value: value[:-len("_IntegrationTest")],
    )


# ----------------------------------------------------------------------
def Test(
    content: str,
    *,
    single_threaded: bool=False,
    quiet: bool=False,
    raise_if_single_exception: bool=True,
) -> Tuple[str, str]:
    dm_and_sink = iter(GenerateDoneManagerAndSink())

    filename = Path("root_file")

    results = Parse(
        cast(DoneManager, next(dm_and_sink)),
        [(filename, lambda: content)],
        single_threaded=single_threaded,
        quiet=quiet,
        raise_if_single_exception=raise_if_single_exception,
    )

    assert len(results) == 1
    assert filename in results
    result = results[filename]
    assert isinstance(result, RootStatement), result

    visitor = ToPythonDictVisitor()

    result.Accept(visitor)

    return rtyaml.dump(visitor.root), cast(str, next(dm_and_sink))
