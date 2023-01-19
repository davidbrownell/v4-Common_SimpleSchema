# ----------------------------------------------------------------------
# |
# |  TestHelpersImpl.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-03 11:16:51
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Implements functionality leveraged across different tests within this module and its descendants"""

import os
import re
import sys

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Match, Set
from unittest import mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx

pytest.register_assert_rewrite("Common_PythonDevelopment.TestHelpers")

from Common_PythonDevelopment.TestHelpers import CompareResultsFromFile as CompareResultsFromFileImpl


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement
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
def ToDict(
    root: RootStatement,
) -> List[Dict[str, Any]]:
    visitor = ToPythonDictVisitor()

    root.Accept(visitor)

    return visitor.root


# ----------------------------------------------------------------------
def ScrubString(
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


# ----------------------------------------------------------------------
@contextmanager
def GenerateMockedPath(
    mocked_content: Dict[str, str],
    initial_filenames: List[str],
    workspace: Path=DEFAULT_WORKSPACE_PATH,
) -> Iterator[
    Dict[
        Path,                               # Workspace
        Dict[
            Path,                           # Relative path
            Callable[[], str],
        ],
    ],
]:
    all_content: Dict[Path, str] = {
        workspace / filename: content
        for filename, content in mocked_content.items()
    }

    fake_dirs: Set[Path] = set()

    for filename in all_content.keys():
        for parent in filename.parents:
            if Path.is_dir(parent):
                break

            fake_dirs.add(parent)

    original_exists = Path.exists
    original_is_dir = Path.is_dir
    original_is_file = Path.is_file
    original_open = Path.open

    # ----------------------------------------------------------------------
    def MockedExists(
        path: Path,
    ) -> bool:
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
    ) -> bool:
        if path in all_content:
            return True

        return original_is_file(path)

    # ----------------------------------------------------------------------
    def MockedOpen(
        path: Path,
        *args,
        **kwargs,
    ):
        original_content = all_content.get(path, None)

        if original_content is not None:
            mock_obj = mock.MagicMock()

            mock_obj.__enter__().read.return_value = original_content

            return mock_obj

        return original_open(path, *args, **kwargs)

    # ----------------------------------------------------------------------

    with mock.patch.object(Path, "exists", side_effect=MockedExists, autospec=True):
        with mock.patch.object(Path, "is_dir", side_effect=MockedIsDir, autospec=True):
            with mock.patch.object(Path, "is_file", side_effect=MockedIsFile, autospec=True):
                with mock.patch.object(Path, "open", side_effect=MockedOpen, autospec=True):
                    yield {
                        workspace: {
                            Path(initial_filename): (lambda filename=initial_filename: all_content[workspace / filename])
                            for initial_filename in initial_filenames
                        },
                    }
