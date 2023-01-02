# ----------------------------------------------------------------------
# |
# |  PseudoStructure_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-27 09:13:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Integration tests that verify the lowering of StructureElements defined as items"""

import sys
import textwrap

from pathlib import Path

import pytest
import rtyaml

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.Range import Range
    from SimpleSchema.Schema.Elements.Expressions.Expression import Expression
    from SimpleSchema.Schema.Elements.Statements.Statement import Statement
    from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement
    from SimpleSchema.Schema.Elements.Types.Type import Type
    from SimpleSchema.Schema.Lower import *
    from SimpleSchema.Schema.Lower.IntegrationTests.Impl import TestHelpers
    from SimpleSchema.Schema.Visitors.ToPythonDictVisitor import ToPythonDictVisitor


# ----------------------------------------------------------------------
def test_TODOPlaceholder():
    # TODO: Remove this when other tests are restored
    assert True


# ----------------------------------------------------------------------
@pytest.mark.parametrize("has_base", [False, True])
def TODOtest_Structure(has_base):
    result = TestHelpers.Test(
        textwrap.dedent(
            """\
            the_item{} ->
                value: Type
            """,
        ).format(": Base" if has_base else ""),
    )[0]

    _Test(
        result,
        suffix="-{}".format(has_base),
    )


# ----------------------------------------------------------------------
@pytest.mark.parametrize("has_base", [False, True])
def TODOtest_StructureWithMetadata(has_base):
    result = TestHelpers.Test(
        textwrap.dedent(
            """\
            the_item{} {{
                value1: 10
                value2: "a string value"
            }} ->
                value: Type
            """,
        ).format(": Base" if has_base else ""),
    )[0]

    _Test(
        result,
        suffix="-{}".format(has_base),
    )


# ----------------------------------------------------------------------
@pytest.mark.parametrize("has_base", [False, True])
def TODOtest_StructureContainer(has_base):
    result = TestHelpers.Test(
        textwrap.dedent(
            """\
            the_item{}* ->
                value: Type
            """,
        ).format(": Base" if has_base else ""),
    )[0]

    _Test(
        result,
        suffix="-{}".format(has_base),
    )


# ----------------------------------------------------------------------
@pytest.mark.parametrize("has_base", [False, True])
def TODOtest_StructureContainerWithMetadata(has_base):
    result = TestHelpers.Test(
        textwrap.dedent(
            """\
            the_item{}* {{
                value1: 10
                value2: "the string value"
            }} ->
                value: Type
            """,
        ).format(": Base" if has_base else ""),
    )[0]

    _Test(
        result,
        suffix="-{}".format(has_base),
    )


# ----------------------------------------------------------------------
def TODOtest_Complex():
    result = TestHelpers.Test(
        textwrap.dedent(
            """\
            foo ->
                single: String
                multiple: String*

            foos* ->
                single: String
                multiple: String* {
                    dictionary: True
                    min_length: 10
                }
            """,
        ),
    )[0]

    assert len(result.statements) == 6

    # foo
    assert result.statements[0].parent is result
    assert result.statements[0].is_disabled is True

    assert result.statements[1].parent is result
    assert result.statements[1].is_disabled is False

    assert result.statements[2].parent is result
    assert result.statements[2].is_disabled is False

    assert len(result.statements[1].children) == 4

    assert result.statements[1].children[0].parent is result.statements[1]
    assert result.statements[1].children[0].is_disabled is False

    assert result.statements[1].children[1].parent is result.statements[1]
    assert result.statements[1].children[1].is_disabled is True

    assert result.statements[1].children[2].parent is result.statements[1]
    assert result.statements[1].children[2].is_disabled is False

    assert result.statements[1].children[3].parent is result.statements[1]
    assert result.statements[1].children[3].is_disabled is False

    # foos
    assert result.statements[3].parent is result
    assert result.statements[3].is_disabled is True

    assert result.statements[4].parent is result
    assert result.statements[4].is_disabled is False

    assert result.statements[5].parent is result
    assert result.statements[5].is_disabled is False

    assert len(result.statements[4].children) == 4

    assert result.statements[4].children[0].parent is result.statements[4]
    assert result.statements[4].children[0].is_disabled is False

    assert result.statements[4].children[1].parent is result.statements[4]
    assert result.statements[4].children[1].is_disabled is True

    assert result.statements[4].children[2].parent is result.statements[4]
    assert result.statements[4].children[2].is_disabled is False

    assert result.statements[4].children[3].parent is result.statements[4]
    assert result.statements[4].children[3].is_disabled is False

    _Test(result)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _Test(
    result: RootStatement,
    *,
    suffix: Optional[str]=None,
) -> None:
    visitor = ToPythonDictVisitor(
        add_disabled_status=True,
    )

    result.Accept(
        visitor,
        include_disabled=True,
    )

    content = rtyaml.dump(visitor.root)

    content = content.replace("workspace\\root_file", "workspace/root_file")

    TestHelpers.CompareResultsFromFile(
        content,
        call_stack_offset=1,
        suffix=suffix,
    )
