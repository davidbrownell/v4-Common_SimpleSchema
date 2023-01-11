# ----------------------------------------------------------------------
# |
# |  Parse_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-03 10:40:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Integration test for Parse"""

import re
import sys
import textwrap

from pathlib import Path
from typing import List, Set, Tuple
from unittest import mock

import pytest
import rtyaml

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.TestHelpers.StreamTestHelpers import GenerateDoneManagerAndSink

pytest.register_assert_rewrite("Common_PythonDevelopment.TestHelpers")

from Common_PythonDevelopment.TestHelpers import CompareResultsFromFile as CompareResultsFromFileImpl


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Parse import *
    from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement
    from SimpleSchema.Schema.Visitors.ToPythonDictVisitor import ToPythonDictVisitor

    from SimpleSchema.Schema.Parse import TestHelpersImpl


# ----------------------------------------------------------------------
def test_ParseItemFundamentalResolution():
    result = _Execute(
        {
            "entry_point": textwrap.dedent(
                """\
                value1: String
                value2: String*
                value3: String { validation_expression: ".*" }
                value4: String { validation_expression: ".*" } *
                value5: String { validation_expression: ".*" } ? { default: "foo" }
                """,
            ),
        },
        ["entry_point", ],
    )

    assert not isinstance(next(iter(result[1].values())), Exception)
    _CompareResultsFromFile(result[1])  # type: ignore


# ----------------------------------------------------------------------
def test_ParseTupleFundamentalResolution():
    result = _Execute(
        {
            "entry_point": textwrap.dedent(
                """\
                value1: (String, )
                value2: (String+, )?
                value3: (String, Integer, Number)
                value4: (String { min_length: 2 }, Integer { min: 32 }, Number { min: 11.0 })
                value5: (String, (String, (String, )), Integer, Boolean)
                """,
            ),
        },
        ["entry_point", ],
    )

    assert not isinstance(next(iter(result[1].values())), Exception)
    _CompareResultsFromFile(result[1])  # type: ignore


# ----------------------------------------------------------------------
def test_ParseVariantFundamentalResolution():
    result = _Execute(
        {
            "entry_point": textwrap.dedent(
                """\
                value1: (String | Number )
                value2: (String+ | Number)?
                value3: (String | Integer | Number)
                value4: (String { min_length: 2 } | Integer { min: 32 } | Number { min: 11.0 })
                value5: (String | (String, (String, )) | Integer | Boolean)
                """,
            ),
        },
        ["entry_point", ],
    )

    assert not isinstance(next(iter(result[1].values())), Exception)
    _CompareResultsFromFile(result[1])  # type: ignore


# ----------------------------------------------------------------------
def test_Aliases():
    result = _Execute(
        {
            "entry_point": textwrap.dedent(
                """\
                CustomType1: String*
                CustomType2: (String | Integer | Boolean)

                value1: CustomType1
                value2: CustomType2
                """,
            ),
        },
        ["entry_point", ],
    )

    assert not isinstance(next(iter(result[1].values())), Exception)
    _CompareResultsFromFile(result[1])  # type: ignore


# ----------------------------------------------------------------------
def test_StructureAliases():
    result = _Execute(
        {
            "entry_point": textwrap.dedent(
                """\
                Struct0 ->
                    pass

                Struct1 ->
                    a: String
                    b: Boolean

                    Struct2 ->
                        d: Number

                    struct0: Struct0
                    struct1: Struct1
                    struct2: Struct2

                value1: Struct1
                value2: Struct1.Struct2
                """,
            ),
        },
        ["entry_point", ],
    )

    assert not isinstance(next(iter(result[1].values())), Exception)
    _CompareResultsFromFile(result[1])  # type: ignore


# ----------------------------------------------------------------------
def test_StructWithBases():
    result = _Execute(
        {
            "entry_point": textwrap.dedent(
                """\
                StructWithFundamentalBase: String ->
                    pass

                StructWithSingleBase: StructWithFundamentalBase ->
                    pass

                StructWithMultipleBases: (StructWithSingleBase, StructWithFundamentalBase) ->
                    pass
                """,
            ),
        },
        ["entry_point", ],
    )

    assert not isinstance(next(iter(result[1].values())), Exception)
    _CompareResultsFromFile(result[1])  # type: ignore


# ----------------------------------------------------------------------
def test_ErrorCircularDependency():
    with pytest.raises(SimpleSchemaException) as exc_info:
        _Execute(
            {
                "entry_point": textwrap.dedent(
                    """\
                    Struct1: Struct2 ->
                        pass

                    Struct2: Struct3 ->
                        pass

                    Struct3: Struct1 ->
                        pass
                    """,
                ),
            },
            ["entry_point", ],
        )

    assert TestHelpersImpl.ScrubString(str(exc_info.value)) == textwrap.dedent(
        """\
        A cycle was detected in 'Struct1':

            - 'Struct1' entry_point <[1, 1] -> [1, 8]>
            - 'Struct2' entry_point <[4, 1] -> [4, 8]>
            - 'Struct3' entry_point <[7, 1] -> [7, 8]>

        entry_point <[1, 1] -> [1, 8]>
        """,
    )


# ----------------------------------------------------------------------
def test_ErrorCircularDependencyViaTuple():
    with pytest.raises(SimpleSchemaException) as exc_info:
        _Execute(
            {
                "entry_point": textwrap.dedent(
                    """\
                    Struct1: Struct2 ->
                        pass

                    Struct2: Struct4 ->
                        pass

                    Struct3 ->
                        pass

                    Struct4: (Struct3, Struct1, ) ->
                        pass
                    """,
                ),
            },
            ["entry_point", ],
        )

    assert TestHelpersImpl.ScrubString(str(exc_info.value)) == textwrap.dedent(
        """\
        A cycle was detected in 'Struct1':

            - 'Struct1' entry_point <[1, 1] -> [1, 8]>
            - 'Struct2' entry_point <[4, 1] -> [4, 8]>
            - 'Struct4' entry_point <[10, 1] -> [10, 8]>
            - 'Struct1 (Tuple index 1)' entry_point <[10, 20] -> [10, 27]>

        entry_point <[1, 1] -> [1, 8]>
        """,
    )




# TODO: FundamentalResolutionWithMetadata
# TODO: ErrorFundamentalResolutionWrongType
# TODO: Validate can convert from int to float

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _Execute(
    content: Dict[str, str],
    initial_filenames: List[str],
    *,
    single_threaded: bool=False,
    quiet: bool=False,
    raise_if_single_exception: bool=True,
) -> Tuple[
    str,
    Dict[str, Union[Exception, RootStatement]],
]:
    with TestHelpersImpl.GenerateMockedPath(content, initial_filenames) as workspaces:
        dm_and_sink = iter(GenerateDoneManagerAndSink())

        results = Parse(
            cast(DoneManager, next(dm_and_sink)),
            workspaces,
            single_threaded=single_threaded,
            quiet=quiet,
            raise_if_single_exception=raise_if_single_exception,
        )

        output = cast(str, next(dm_and_sink))

        exceptions: Dict[str, Exception] = {}
        normalized_results: Dict[str, RootStatement] = {}

        for content_name, result in results.items():
            content_name = content_name.as_posix()

            if isinstance(result, Exception):
                exceptions[content_name] = result
            else:
                normalized_results[content_name] = result

        if exceptions:
            if raise_if_single_exception and len(exceptions) == 1:
                raise next(iter(exceptions.values()))

            return output, exceptions  # type: ignore

        return output, normalized_results  # type: ignore


# ----------------------------------------------------------------------
def _CompareResultsFromFile(
    results: Dict[str, RootStatement],
    *,
    call_stack_offset: int=0,
) -> None:
    # ----------------------------------------------------------------------
    def ToDict(
        root: RootStatement,
    ) -> List[Dict[str, Any]]:
        visitor = ToPythonDictVisitor()

        root.Accept(visitor)

        return visitor.root

    # ----------------------------------------------------------------------

    dict_content: Dict[str, List[Dict[str, Any]]] = {
        key: ToDict(value)
        for key, value in results.items()
    }

    TestHelpersImpl.CompareResultsFromFile(
        TestHelpersImpl.ScrubString(rtyaml.dump(dict_content)),
        call_stack_offset=call_stack_offset + 1,
    )
