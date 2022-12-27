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

import os
import re
import sys

from dataclasses import dataclass
from pathlib import Path
from typing import Match, Set
from unittest import mock

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
    from SimpleSchema.Schema.Parse import *  # pylint: disable=unused-wildcard-import,wildcard-import
    from SimpleSchema.Schema.Visitors.ToPythonDictVisitor import ToPythonDictVisitor


# ----------------------------------------------------------------------
DEFAULT_WORKSPACE_PATH                      = Path(__file__).parent.parent


# ----------------------------------------------------------------------
def CompareResultsFromFile(
    content: str,
    call_stack_offset: int=0,
) -> None:
    CompareResultsFromFileImpl(
        content,
        file_extension=".yaml",
        call_stack_offset=call_stack_offset + 1,
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
    filename = DEFAULT_WORKSPACE_PATH / "root_file"

    result = TestMultiple(
        {filename: content},
        [filename],
        single_threaded=single_threaded,
        quiet=quiet,
        raise_if_single_exception=raise_if_single_exception,
    )

    assert len(result.dict_results) == 1
    assert filename in result.dict_results

    yaml_result = ScrubYamlString(rtyaml.dump(result.dict_results[filename]))

    return yaml_result, result.output


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class MultipleReturnValue(object):
    dict_results: Dict[Path, Union[Exception, List[Dict[str, Any]]]]
    output: str


def TestMultiple(
    all_content: Dict[Path, str],
    initial_filenames: List[Path],
    *,
    single_threaded: bool=False,
    quiet: bool=False,
    raise_if_single_exception: bool=True,
) -> MultipleReturnValue:
    workspace_name = DEFAULT_WORKSPACE_PATH

    all_content = {
        workspace_name / filename: content
        for filename, content in all_content.items()
    }

    initial_filenames = [workspace_name / filename for filename in initial_filenames]

    original_exists = Path.exists
    original_is_dir = Path.is_dir
    original_is_file = Path.is_file
    original_open = Path.open

    fake_dirs: Set[Path] = set()

    for filename in all_content.keys():
        for parent in filename.parents:
            if os.path.isdir(parent):
                break

            fake_dirs.add(parent)

    # ----------------------------------------------------------------------
    def MockedExists(
        path: Path,
    ):
        if path in all_content or path in fake_dirs:
            return True

        return original_exists(path)

    # ----------------------------------------------------------------------
    def MockedIsDir(
        path: Path,
    ) -> bool:
        if path in fake_dirs:
            return True

        return original_is_dir(path)

    # ----------------------------------------------------------------------
    def MockedIsFile(
        path: Path,
    ):
        if path in all_content:
            return True

        return original_is_file(path)

    # ----------------------------------------------------------------------
    def MockedOpen(path, *args, **kwargs):
        if path not in all_content:
            return original_open(path, *args, **kwargs)

        assert path in all_content, path

        mock_obj = mock.MagicMock()

        mock_obj.__enter__().read.return_value = all_content[path]

        return mock_obj

    # ----------------------------------------------------------------------

    with mock.patch.object(Path, "exists", side_effect=MockedExists, autospec=True):
        with mock.patch.object(Path, "is_dir", side_effect=MockedIsDir, autospec=True):
            with mock.patch.object(Path, "is_file", side_effect=MockedIsFile, autospec=True):
                with mock.patch.object(Path, "open", side_effect=MockedOpen, autospec=True):
                    dm_and_sink = iter(GenerateDoneManagerAndSink())

                    parse_results = Parse(
                        cast(DoneManager, next(dm_and_sink)),
                        {
                            workspace_name: {
                                initial_filename: (lambda filename=initial_filename: all_content[filename])
                                for initial_filename in initial_filenames
                            }
                        },
                        single_threaded=single_threaded,
                        quiet=quiet,
                        raise_if_single_exception=raise_if_single_exception,
                    )

                    output = cast(str, next(dm_and_sink))

    # ----------------------------------------------------------------------
    def ToDict(
        root: RootStatement,
    ) -> List[Dict[str, Any]]:
        visitor = ToPythonDictVisitor()

        root.Accept(visitor)

        return visitor.root

    # ----------------------------------------------------------------------

    assert len(parse_results) == 1, parse_results
    assert workspace_name in parse_results

    parse_results = parse_results[workspace_name]

    return MultipleReturnValue(
        {
            filename: ToDict(parse_result) if isinstance(parse_result, RootStatement) else parse_result
            for filename, parse_result in parse_results.items()
        },
        output,
    )


# ----------------------------------------------------------------------
def ScrubYamlString(
    content: str,
) -> str:
    # Process the results. rtyaml will break range statement into multiple lines at arbitrary
    # positions based on the length of the workspace name, which makes it difficult to create
    # expected output that is consistent in a variety of different scenarios. Normalize this
    # content by looking for ranges and recreating them on the fly.
    range_regex = re.compile(
        r"""(?#
        Whitespace prefix                   )\s+(?#
        Range Begin                         )<\s*(?#
            Start Begin                     )\[\s*(?#
                Line                        )(?P<start_line>\d+)\s*(?#
                Sep                         ),\s*(?#
                Column                      )(?P<start_col>\d+)\s*(?#
            Start End                       )\]\s*(?#
            Sep                             )->\s*(?#
            End Begin                       )\[\s*(?#
                Line                        )(?P<end_line>\d+)\s*(?#
                Sep                         ),\s*(?#
                Column                      )(?P<end_col>\d+)\s*(?#
            End End                         )\]\s*(?#
        Range End                           )>(?#
        )""",
        re.DOTALL,
    )

    sep_sentinel = "__<<SEP>>__"
    assert sep_sentinel == re.escape(sep_sentinel)

    workspace_regex_string = (
        re.escape(
            str(DEFAULT_WORKSPACE_PATH)
                .replace("/", sep_sentinel)
                .replace("\\", sep_sentinel)
        )
        .replace(sep_sentinel, "[/\\\\]")
    )

    filename_regex = re.compile(
        r"""(?#
        Workspace Name                      ){workspace}(?#
        Sep                                 )[/\\\\](?#
        Filename                            )(?P<filename>\S+)(?#
        )""".format(
            workspace=workspace_regex_string,
        ),
    )

    # ----------------------------------------------------------------------
    def ReplaceRange(
        match: Match,
    ) -> str:
        return " <[{}, {}] -> [{}, {}]>".format(
            match.group("start_line"),
            match.group("start_col"),
            match.group("end_line"),
            match.group("end_col"),
        )

    # ----------------------------------------------------------------------
    def ReplaceFilename(
        match: Match,
    ) -> str:
        return match.group("filename").replace(os.path.sep, "/")

    # ----------------------------------------------------------------------

    content = range_regex.sub(ReplaceRange, content)
    content = filename_regex.sub(ReplaceFilename, content)

    return content
