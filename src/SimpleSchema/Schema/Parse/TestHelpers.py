# ----------------------------------------------------------------------
# |
# |  TestHelpers.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-20 13:38:25
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
from typing import Any, Callable, Iterator, Match, Optional, Set
from unittest.mock import MagicMock as Mock, patch

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Types import overridemethod

pytest.register_assert_rewrite("Common_PythonDevelopment.TestHelpers")

from Common_PythonDevelopment.TestHelpers import CompareResultsFromFile as CompareResultsFromFileImpl


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Element import Element, VisitResult
    from SimpleSchema.Schema.Elements.Common.SimpleElement import SimpleElement

    from SimpleSchema.Schema.Elements.Expressions.BooleanExpression import BooleanExpression
    from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
    from SimpleSchema.Schema.Elements.Expressions.ListExpression import ListExpression
    from SimpleSchema.Schema.Elements.Expressions.NoneExpression import NoneExpression
    from SimpleSchema.Schema.Elements.Expressions.NumberExpression import NumberExpression
    from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression
    from SimpleSchema.Schema.Elements.Expressions.TupleExpression import TupleExpression

    from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement

    from SimpleSchema.Schema.Parse.ANTLR.Elements.Common.ParseIdentifier import ParseIdentifier

    from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseIncludeStatement import ParseIncludeStatement
    from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseItemStatement import ParseItemStatement

    from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseIdentifierType import ParseIdentifierType

    from SimpleSchema.Schema.Parse.Visitor import Visitor


# ----------------------------------------------------------------------
DEFAULT_WORKSPACE_PATH                      = Path(__file__).parent


# ----------------------------------------------------------------------
def CompareResultsFromFile(
    content: str,
    call_stack_offset: int=0,
) -> None:
    # ----------------------------------------------------------------------
    def DecorateStem(
        value: str,
    ) -> str:
        for test_name in ["_IntegrationTest", "_UnitTest"]:
            if value.endswith(test_name):
                return value[:-len(test_name)]

        return value

    # ----------------------------------------------------------------------

    CompareResultsFromFileImpl(
        content,
        file_extension=".yaml",
        call_stack_offset=call_stack_offset + 1,
        decorate_test_name_func=lambda value: value[len("test_"):],
        decorate_stem_func=DecorateStem,
    )


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
            Line                            )Ln\s+(?P<start_line>\d+)\s*(?#
            Sep                             ),\s*(?#
            Column                          )Col\s+(?P<start_col>\d+)\s*(?#
            Sep                             )->\s*(?#
            Line                            )Ln\s+(?P<end_line>\d+)\s*(?#
            Sep                             ),\s*(?#
            Column                          )Col\s+(?P<end_col>\d+)\s*(?#
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
        return " <Ln {}, Col {} -> Ln {}, Col {}>".format(
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

    content = content.replace("\\", "/")

    return content


# ----------------------------------------------------------------------
def ToDict(
    root: RootStatement,
) -> list[dict[str, Any]]:
    visitor = _ToPythonDictVisitor()

    root.Accept(visitor)

    return visitor.root


# ----------------------------------------------------------------------
@contextmanager
def GenerateMockedPath(
    mocked_content: dict[str, str],
    initial_filenames: list[str],
    workspace: Path=DEFAULT_WORKSPACE_PATH,
) -> Iterator[
    dict[
        Path,                               # Workspace
        dict[
            Path,                           # Relative path
            Callable[[], str],
        ],
    ],
]:
    all_content: dict[Path, str] = {
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
            mock_obj = Mock()

            mock_obj.__enter__().read.return_value = original_content

            return mock_obj

        return original_open(path, *args, **kwargs)

    # ----------------------------------------------------------------------

    with patch.object(Path, "exists", side_effect=MockedExists, autospec=True):
        with patch.object(Path, "is_dir", side_effect=MockedIsDir, autospec=True):
            with patch.object(Path, "is_file", side_effect=MockedIsFile, autospec=True):
                with patch.object(Path, "open", side_effect=MockedOpen, autospec=True):
                    yield {
                        workspace: {
                            Path(initial_filename): (lambda filename=initial_filename: all_content[workspace / filename])
                            for initial_filename in initial_filenames
                        },
                    }


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _ToPythonDictVisitor(Visitor):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        *,
        include_disabled_status: bool=False,
    ):
        super(_ToPythonDictVisitor, self).__init__()

        self.include_disabled_status        = include_disabled_status

        self._stack: list[dict[str, Any]]               = []
        self._processing_reference_element_ctr          = 0

    # ----------------------------------------------------------------------
    @property
    def root(self) -> list[dict[str, Any]]:
        assert len(self._stack) == 1, self._stack
        return self._stack

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnElement(self, element: Element) -> Iterator[Optional[VisitResult]]:
        self._stack.append(
            {
                "__type__": element.__class__.__name__,
                "range": str(element.range),
            },
        )

        if self.include_disabled_status:
            self._stack[-1]["__disabled__"] = element.is_disabled

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnElementChildren(self, element: Element) -> Iterator[Optional[VisitResult]]:
        prev_num_items = len(self._stack)

        yield

        children = self._stack[prev_num_items:]
        self._stack = self._stack[:prev_num_items]

        d = self._stack[-1]

        d[element.CHILDREN_NAME] = children

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnElementDetailsItem(self, name: str, element_or_elements: Element.GenerateAcceptDetailsGeneratorItemsType) -> Iterator[Optional[VisitResult]]:
        is_list = isinstance(element_or_elements, list)
        prev_num_items = len(self._stack)

        yield

        items = self._stack[prev_num_items:]
        self._stack = self._stack[:prev_num_items]

        if not is_list:
            assert len(items) == 1
            items = items[0]

        self._stack[-1][name] = items

    # ----------------------------------------------------------------------
    # |
    # |  Common
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnParseIdentifier(self, element: ParseIdentifier) -> Iterator[Optional[VisitResult]]:
        self._stack[-1]["value"] = element.value
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnSimpleElement(self, element: SimpleElement) -> Iterator[Optional[VisitResult]]:
        value = element.value

        if isinstance(value, Path):
            value = str(value)

        self._stack[-1]["value"] = value
        yield

    # ----------------------------------------------------------------------
    # |
    # |  Expressions
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnBooleanExpression(self, element: BooleanExpression) -> Iterator[Optional[VisitResult]]:
        self._stack[-1]["value"] = element.value
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnIntegerExpression(self, element: IntegerExpression) -> Iterator[Optional[VisitResult]]:
        self._stack[-1]["value"] = element.value
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnListExpression(self, element: ListExpression) -> Iterator[Optional[VisitResult]]:
        prev_num_items = len(self._stack)

        for child in element.value:
            visit_result = child.Accept(self)
            if visit_result == VisitResult.Terminate:
                yield visit_result
                return

        children = self._stack[prev_num_items:]
        self._stack = self._stack[:prev_num_items]

        self._stack[-1]["value"] = children

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnNoneExpression(self, element: NoneExpression) -> Iterator[Optional[VisitResult]]:
        self._stack[-1]["value"] = element.value
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnNumberExpression(self, element: NumberExpression) -> Iterator[Optional[VisitResult]]:
        self._stack[-1]["value"] = element.value
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnStringExpression(self, element: StringExpression) -> Iterator[Optional[VisitResult]]:
        self._stack[-1]["value"] = element.value
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnTupleExpression(self, element: TupleExpression) -> Iterator[Optional[VisitResult]]:
        prev_num_items = len(self._stack)

        for child in element.value:
            visit_result = child.Accept(self)
            if visit_result == VisitResult.Terminate:
                yield visit_result
                return

        children = self._stack[prev_num_items:]
        self._stack = self._stack[:prev_num_items]

        self._stack[-1]["value"] = children

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    # |
    # |  Statements
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnParseIncludeStatement(self, element: ParseIncludeStatement) -> Iterator[Optional[VisitResult]]:
        self._stack[-1]["include_type"] = str(element.include_type)
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnParseItemStatement(self, element: ParseItemStatement) -> Iterator[Optional[VisitResult]]:
        self._stack[-1]["visibility"] = str(element.name.visibility.value)
        yield

    # ----------------------------------------------------------------------
    # |
    # |  Types
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnParseIdentifierType(self, element: ParseIdentifierType) -> Iterator[Optional[VisitResult]]:
        if element.is_global_reference:
            self._stack[-1]["is_global_reference"] = str(element.is_global_reference)
        if element.is_item_reference:
            self._stack[-1]["is_item_reference"] = str(element.is_item_reference)

        yield
