# ----------------------------------------------------------------------
# |
# |  IncludeStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-19 11:52:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Integration tests for include statements"""

import re
import sys
import textwrap

from pathlib import Path
from typing import Dict, List

import pytest
import rtyaml

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException
    from SimpleSchema.Schema.Parse.IntegrationTests.Impl.TestHelpers import CompareResultsFromFile, TestMultiple, MultipleReturnValue, ScrubYamlString, DEFAULT_WORKSPACE_PATH



# ----------------------------------------------------------------------
def test_SingleFile():
    _Test(
        {
            "root_file": textwrap.dedent(
                """\
                from include_file1 import Foo
                """,
            ),
            "include_file1" : textwrap.dedent(
                """\
                Foo: String
                """,
            ),
        },
        ["root_file", ],
    )


# ----------------------------------------------------------------------
def test_SingleFileWithExtension():
    _Test(
        {
            "root_file": textwrap.dedent(
                """\
                from include_file1 import Foo
                """,
            ),
            "include_file1.SimpleSchema": textwrap.dedent(
                """\
                Foo: String
                """,
            ),
        },
        ["root_file", ],
    )


# ----------------------------------------------------------------------
def test_SingleFileRenamed():
    _Test(
        {
            "root_file": textwrap.dedent(
                """\
                from include_file1 import Foo as RenamedFoo
                from include_file2 import Bar as RenamedBar
                """,
            ),
            "include_file1": textwrap.dedent(
                """\
                Foo: String
                """,
            ),
            "include_file2.SimpleSchema": textwrap.dedent(
                """\
                Bar: Integer
                """,
            ),
        },
        ["root_file", ],
    )


# ----------------------------------------------------------------------
def test_RelativeImport():
    _Test(
        {
            "dir/root_file": textwrap.dedent(
                """\
                from ../include_file import Foo
                """,
            ),
            "dir/include_file": textwrap.dedent(
                """\
                ThisShouldNotBeImported: String
                """,
            ),
            "include_file": textwrap.dedent(
                """\
                ValidImport: String
                """,
            ),
        },
        ["dir/root_file", ],
    )


# ----------------------------------------------------------------------
def test_DirectoryImport():
    _Test(
        {
            "root_file": textwrap.dedent(
                """\
                from dir import ImportedFile1
                from dir import ImportedFile2
                """,
            ),
            "dir/ImportedFile1": textwrap.dedent(
                """\
                Type1: String
                """,
            ),
            "dir/ImportedFile2.SimpleSchema": textwrap.dedent(
                """\
                Type2: String
                """,
            ),
        },
        ["root_file", ],
    )


# ----------------------------------------------------------------------
def test_MultipleImports():
    _Test(
        {
            "root_file": textwrap.dedent(
                """\
                from include_file import One as One1, Two, Three as Three3, Four
                """,
            ),
            "include_file": textwrap.dedent(
                """\
                """,
            ),
        },
        ["root_file", ],
    )


# ----------------------------------------------------------------------
def test_MultipleGroupImports():
    _Test(
        {
            "root_file": textwrap.dedent(
                """\
                from include_file import (
                    One,
                        Two as Two2,
                        Three


                        ,
                    Four as Four4,
                )
                """,
            ),
            "include_file": textwrap.dedent(
                """\
                """,
            ),
        },
        ["root_file", ],
    )


# ----------------------------------------------------------------------
def test_ErrorInvalidFile():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape(
            "'this_is_not_a_valid_file_or_dir' is not a recognized file or directory. ({} <[1, 6] -> [1, 37]>)".format(
                DEFAULT_WORKSPACE_PATH / "root_item",
            ),
        ),
    ):
        TestMultiple(
            {
                Path("root_item"): textwrap.dedent(
                    """\
                    from this_is_not_a_valid_file_or_dir import Foo
                    """,
                ),
            },
            [Path("root_item"), ],
            quiet=True,
        )


# ----------------------------------------------------------------------
def test_ErrorMultpleImportItemsWithDirectory():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape(
            "A single filename must be imported when including content from a directory. ({} <[3, 29] -> [3, 39]>)".format(
                DEFAULT_WORKSPACE_PATH / "root_item",
            ),
        ),
    ):
        TestMultiple(
            {
                Path("root_item"): textwrap.dedent(
                    """\
                    from dir import ValidFile1              # works
                    from dir import ValidFile2              # works
                    from dir import ValidFile1, ValidFile2  # error
                    """,
                ),
                Path("dir/ValidFile1"): "",
                Path("dir/ValidFile2"): "",
            },
            [Path("root_item"), ],
            quiet=True,
        )


# ----------------------------------------------------------------------
def test_ErrorInvalidFileWithinDirectory():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape(
            "'InvalidFile' is not a recognized filename. ({} <[2, 6] -> [2, 28]>)".format(
                DEFAULT_WORKSPACE_PATH / "root_item",
            ),
        ),
    ):
        TestMultiple(
            {
                Path("root_item"): textwrap.dedent(
                    """\
                    from dir import ValidFile       # works
                    from dir import InvalidFile     # error
                    """,
                ),
                Path("dir/ValidFile"): "",
            },
            [Path("root_item"), ],
            quiet=True,
        )


# ----------------------------------------------------------------------
def test_ErrorNotADescendant():
    non_workspace_file = PathEx.EnsureFile(Path(__file__).parent.parent / "__init__.py")

    non_workspace_file = Path(*(("/", ) + non_workspace_file.parts[1:]))
    assert non_workspace_file.is_file(), non_workspace_file

    with pytest.raises(
        SimpleSchemaException,
        match=re.escape(
            "The included file '{}' is not a descendant of any workspace. ({} <[1, 1] -> [2, 1]>)".format(
                non_workspace_file.resolve(),
                DEFAULT_WORKSPACE_PATH / "root_item",
            ),
        ),
    ):
        TestMultiple(
            {
                Path("root_item"): textwrap.dedent(
                    """\
                    from {} import IgnoreMe
                    """,
                ).format(
                    non_workspace_file.as_posix(),
                ),
            },
            [Path("root_item"), ],
            quiet=True,
        )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _Test(
    file_contents: Dict[str, str],
    initial_filenames: List[str],
) -> None:
    # Invoke
    results = TestMultiple(
        {
            Path(filename): content
            for filename, content in file_contents.items()
        },
        [Path(initial_filename) for initial_filename in initial_filenames],
    )

    # Combine the results
    results = ScrubYamlString(
        rtyaml.dump(
            {
                # Don't wait for ScrubYamlString to replace the filename contents within the yaml
                # string, as long strings will cause the format to change; remove the common
                # filename paths before converting to yaml.
                (
                    PathEx.CreateRelativePath(DEFAULT_WORKSPACE_PATH, filename)
                        if PathEx.IsDescendant(filename, DEFAULT_WORKSPACE_PATH)
                            else filename
                ).as_posix(): content
                for filename, content in results.dict_results.items()
            },
        ),
    )

    CompareResultsFromFile(
        results,
        call_stack_offset=1,
    )
