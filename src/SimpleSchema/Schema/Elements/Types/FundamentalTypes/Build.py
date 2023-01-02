# ----------------------------------------------------------------------
# |
# |  Build.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-30 07:47:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Builds fundamental types"""

import re
import sys
import textwrap

from contextlib import contextmanager
from enum import auto, Enum
from io import StringIO
from pathlib import Path
from typing import Any, Callable, cast, Dict, Iterator, List, Optional, Set, TextIO, Tuple, Union

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Streams.DoneManager import DoneManager, DoneManagerFlags
from Common_Foundation.Streams.StreamDecorator import StreamDecorator
from Common_Foundation import TextwrapEx
from Common_Foundation.Types import overridemethod

from Common_FoundationEx.BuildImpl import BuildInfoBase
from Common_FoundationEx import ExecuteTasks


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException
    from SimpleSchema.Schema.Elements.Expressions.BooleanExpression import BooleanExpression
    from SimpleSchema.Schema.Elements.Expressions.Expression import Expression
    from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
    from SimpleSchema.Schema.Elements.Expressions.ListExpression import ListExpression
    from SimpleSchema.Schema.Elements.Expressions.NumberExpression import NumberExpression
    from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression
    from SimpleSchema.Schema.Elements.Expressions.TupleExpression import TupleExpression
    from SimpleSchema.Schema.Elements.Statements.ExtensionStatement import ExtensionStatement
    from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement
    from SimpleSchema.Schema.Parse import Parse
    from SimpleSchema.Schema.Parse.ParseElements.Statements.ParseItemStatement import ParseItemStatement
    from SimpleSchema.Schema.Parse.ParseElements.Statements.ParseStructureStatement import ParseStructureStatement
    from SimpleSchema.Schema.Parse.ParseElements.Types.ParseIdentifierType import ParseIdentifierType
    from SimpleSchema.Schema.Visitors.Visitor import Visitor, VisitResult


# ----------------------------------------------------------------------
class BuildInfo(BuildInfoBase):
    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class BuildStep(Enum):
        Building                            = 0
        Generating                          = auto()

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(BuildInfo, self).__init__(
            name="FundamentalTypes",
            requires_output_dir=False,
            required_development_configurations=[
                re.compile("dev"),
            ],
            disable_if_dependency_environment=True,
        )

    # ----------------------------------------------------------------------
    @overridemethod
    def GetNumBuildSteps(
        self,
        configuration: Optional[str],  # pylint: disable=unused-argument
    ) -> int:
        return len(self.__class__.BuildStep)

    # ----------------------------------------------------------------------
    @overridemethod
    def Clean(                              # pylint: disable=arguments-differ
        self,
        configuration: Optional[str],       # pylint: disable=unused-argument
        output_dir: Optional[Path],
        output_stream: TextIO,
        on_progress_update: Callable[       # pylint: disable=unused-argument
            [
                int,                        # Step ID
                str,                        # Status info
            ],
            bool,                           # True to continue, False to terminate
        ],
        *,
        is_verbose: bool,
        is_debug: bool,
    ) -> Union[
        int,                                # Error code
        Tuple[int, str],                    # Error code and short text that provides info about the result
    ]:
        assert output_dir is None, output_dir
        output_dir = self.__class__._CreateOutputDir()  # pylint: disable=protected-access

        with DoneManager.Create(
            output_stream,
            "Cleaning '{}'...".format(output_dir),
            output_flags=DoneManagerFlags.Create(verbose=is_verbose, debug=is_debug),
        ) as dm:
            if not output_dir.is_dir():
                dm.WriteInfo("The directory '{}' does not exist.\n".format(output_dir))
            else:
                PathEx.RemoveTree(output_dir)

        return 0

    # ----------------------------------------------------------------------
    @overridemethod
    def Build(                              # pylint: disable=arguments-differ
        self,
        configuration: Optional[str],       # pylint: disable=unused-argument
        output_dir: Optional[Path],
        output_stream: TextIO,
        on_progress_update: Callable[
            [
                int,                        # Step ID
                str,                        # Status info
            ],
            bool,                           # True to continue, False to terminate
        ],
        *,
        is_verbose: bool,
        is_debug: bool,
        force: bool=False,                  # pylint: disable=unused-argument
    ) -> Union[
        int,                                # Error code
        Tuple[int, str],                    # Error code and short text that provides info about the result
    ]:
        assert output_dir is None, output_dir
        output_dir = self.__class__._CreateOutputDir()  # pylint: disable=protected-access

        roots: Optional[Dict[Path, RootStatement]] = None

        with self.__class__.YieldDoneManager(
            output_stream,
            "Building...",
            is_verbose=is_verbose,
            is_debug=is_debug,
        ) as dm:
            with dm.Nested(
                "Parsing...",
                suffix="\n",
            ) as parse_dm:
                on_progress_update(self.__class__.BuildStep.Building.value, "Building...")

                # ----------------------------------------------------------------------
                def GetContent(
                    filename: Path,
                ) -> str:
                    with filename.open() as f:
                        return f.read()

                # ----------------------------------------------------------------------

                simple_schema_dir = PathEx.EnsureDir(Path(__file__).parent / "SimpleSchema")

                workspaces: Dict[Path, Dict[Path, Callable[[], str]]] = {
                    simple_schema_dir: {
                        Path(child.name): (lambda child=child: GetContent(child))
                        for child in simple_schema_dir.iterdir()
                        if child.suffix == ".SimpleSchema"
                    },
                }

                results = Parse(
                    parse_dm,
                    workspaces,
                    quiet=True,
                )

                assert len(results) == 1, results
                results = next(iter(results.values()))

                for filename, result in results.items():
                    if isinstance(result, Exception):
                        parse_dm.WriteError("{}: {}\n\n".format(filename, result))

                if parse_dm.result != 0:
                    return parse_dm.result

                roots = cast(Dict[Path, RootStatement], results)

            with dm.Nested("Generating...") as generate_dm:
                on_progress_update(self.__class__.BuildStep.Generating.value, "Generating...")

                init_filename = output_dir / "__init__.py"

                if not init_filename.is_file():
                    output_dir.mkdir(parents=True, exist_ok=True)

                    with init_filename.open("w") as f:
                        pass

                # ----------------------------------------------------------------------
                def Execute(
                    context: Tuple[Path, RootStatement],
                    on_simple_status_func: Callable[[str], None],  # pylint: disable=unused-argument
                ) -> Tuple[Optional[int], ExecuteTasks.TransformStep2FuncType[None]]:
                    filename, root = context
                    del context

                    # ----------------------------------------------------------------------
                    def Impl(
                        status: ExecuteTasks.Status,  # pylint: disable=unused-argument
                    ) -> Tuple[None, Optional[str]]:
                        visitor = _Visitor()

                        root.Accept(visitor)

                        output_filename = output_dir / "{}Type.py".format(filename.stem)

                        with output_filename.open("w") as f:
                            f.write(_GenerateHeader())
                            f.write(
                                textwrap.dedent(
                                    """\
                                    # pylint: disable=missing-module-docstring
                                    # pylint: disable=missing-class-docstring

                                    """,
                                ),
                            )

                            lines = visitor.content.split("\n")

                            for line_index, line in enumerate(lines):
                                if line.isspace():
                                    lines[line_index] = ""

                            f.write("\n".join(lines))

                        return None, None

                    # ----------------------------------------------------------------------

                    return None, Impl

                # ----------------------------------------------------------------------

                ExecuteTasks.Transform(
                    generate_dm,
                    "Processing",
                    [
                        ExecuteTasks.TaskData(str(filename), (filename, root))
                        for filename, root in roots.items()
                    ],
                    Execute,
                )

                if parse_dm.result != 0:
                    return parse_dm.result

            return dm.result

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateOutputDir() -> Path:
        return PathEx.EnsureDir(Path(__file__).parent / "GeneratedCode")


# ----------------------------------------------------------------------
# |
# |  Private Types
# |
# ----------------------------------------------------------------------
class _Visitor(Visitor):
    # ----------------------------------------------------------------------
    def __init__(self):
        self._sink                                      = StringIO()
        self._stream_stack: List[StreamDecorator]       = [StreamDecorator(self._sink), ]
        self._header_stack: List[StringIO]              = []
        self._post_init_stack: List[StringIO]           = []

        self._includes: Dict[str, Set[str]]             = {
            "dataclasses": set(["dataclass", ]),
            "enum": set(),
            "typing": set(),
            "SimpleSchema.Schema.Elements.Types.Type": set(["Type", ]),
        }

    # ----------------------------------------------------------------------
    @property
    def content(self) -> str:
        assert len(self._stream_stack) == 1

        includes: List[str] = []

        for include_source, include_items in self._includes.items():
            if not include_items:
                continue

            include_items = list(include_items)
            include_items.sort()

            includes.append(
                "from {} import {}".format(include_source, ", ".join(include_items)),
            )

        return textwrap.dedent(
            """\
            {}


            {}
            """,
        ).format(
            "\n".join(includes),
            self._sink.getvalue().rstrip(),
        )

    # ----------------------------------------------------------------------
    @contextmanager
    def OnRootStatement(self, *args, **kwargs) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnParseStructureStatement(
        self,
        element: ParseStructureStatement,
    ) -> Iterator[Optional[VisitResult]]:
        if element.base is None:
            raise SimpleSchemaException("Structures must have a base.", element.range)

        if not isinstance(element.base, ParseIdentifierType):
            raise SimpleSchemaException("Structures must have an identifier base type.", element.base.range)

        if len(element.base.identifiers) != 1 or element.base.identifiers[0].id.value != "Type":
            raise SimpleSchemaException("The base type for structures must be 'Type'.", element.base.range)

        if element.name.id.value == "Enum":
            # Enums are a bit more complicated than what I'd like to automate at this point.
            self._includes.setdefault("typing", set()).add("List")
            self._includes["typing"].add("Tuple")
            self._includes["typing"].add("Union")
            self._includes.setdefault("SimpleSchema.Schema.Elements.Common.SimpleSchemaException", set()).add("SimpleSchemaException")

            self._stream_stack[-1].write(
                textwrap.dedent(
                    """\
                    # ----------------------------------------------------------------------
                    @dataclass(frozen=True)
                    class EnumType(Type):
                        _EnumItemType = Union[int, str]

                        values: Union[
                            List[_EnumItemType],
                            List[Tuple[_EnumItemType, str]],
                        ]

                        # ----------------------------------------------------------------------
                        def __post_init__(self):
                            if not self.values:
                                raise SimpleSchemaException("Enum values must be provided.", self.range)

                            if isinstance(self.values[0], tuple):
                                get_value_func = lambda v: v[0]
                            else:
                                get_value_func = lambda v: v

                            if isinstance(get_value_func(self.values[0]), int):
                                for value_index, value in enumerate(self.values):
                                    if not isinstance(get_value_func(value), int):
                                        raise SimpleSchemaException("An integer was expected (index: {}).".format(value_index), self.range)

                            elif isinstance(get_value_func(self.values[0]), str):
                                for value_index, value in enumerate(self.values):
                                    if not isinstance(get_value_func(value), str):
                                        raise SimpleSchemaException("A string was expected (index: {}).".format(value_index), self.range)

                            else:
                                assert False, get_value_func(self.values[0])  # pragma: no cover
                    """,
                ),
            )

            yield VisitResult.SkipAll
            return

        self._stream_stack[-1].write(
            textwrap.dedent(
                """\
                # ----------------------------------------------------------------------
                @dataclass(frozen=True)
                class {}Type(Type):
                """,
            ).format(element.name.id.value),
        )

        if not element.cardinality.is_single:
            raise SimpleSchemaException("Structures must be single elements.\n", element.cardinality.range)

        if element.metadata:
            raise SimpleSchemaException("Structures may not have metadata.", element.range)

        if not element.children:
            header_content = ""
            post_init_content = ""
            content = "pass\n"

            yield

        else:
            content_sink = StringIO()
            header_sink = StringIO()
            post_init_sink = StringIO()

            self._stream_stack.append(content_sink)  # type: ignore
            self._header_stack.append(header_sink)
            self._post_init_stack.append(post_init_sink)

            with ExitStack(
                self._stream_stack.pop,
                self._header_stack.pop,
                self._post_init_stack.pop,
            ):
                yield

            header_content = header_sink.getvalue()
            post_init_content = post_init_sink.getvalue()
            content = content_sink.getvalue()

        indented_stream = StreamDecorator(self._stream_stack[-1], line_prefix="    ")

        if header_content:
            indented_stream.write(header_content)

        assert content
        indented_stream.write(content)

        if post_init_content:
            self._includes.setdefault("SimpleSchema.Schema.Elements.Common.SimpleSchemaException", set()).add("SimpleSchemaException")

            indented_stream.write(
                textwrap.dedent(
                    """\

                    # ----------------------------------------------------------------------
                    def __post_init__(self):
                        {}
                    """,
                ).format(
                    TextwrapEx.Indent(post_init_content, 4, skip_first_line=True),
                ),
            )

    # ----------------------------------------------------------------------
    @contextmanager
    def OnParseItemStatement(
        self,
        element: ParseItemStatement,
    ) -> Iterator[Optional[VisitResult]]:
        name = element.name.id.value

        if not isinstance(element.type, ParseIdentifierType):
            raise SimpleSchemaException("Item types must be identifiers.", element.type.range)

        if len(element.type.identifiers) != 1:
            raise SimpleSchemaException("Item types cannot be nested.", element.type.range)

        if element.type.is_element_reference is not None:
            raise SimpleSchemaException("Item types cannot be element references.", element.type.is_element_reference)

        the_type = element.type.identifiers[0].id.value

        if the_type == "Boolean":
            the_type = "bool"
        elif the_type == "Integer":
            the_type = "int"
        elif the_type == "Number":
            the_type = "float"
        elif the_type == "String":
            the_type = "str"
        elif the_type == "Enum":
            the_type = "{}Enum".format(name)
        else:
            assert False, the_type  # pragma: no cover

        potential_metadata_item_prefix: Optional[str] = None

        if element.type.cardinality.is_optional:
            self._includes.setdefault("dataclasses", set()).add("field")
            self._includes.setdefault("typing", set()).add("Optional")

            the_type = "Optional[{}]".format(the_type)

            has_default = False

            if element.type.cardinality.metadata is not None:
                for metadata_item, metadata_value in element.type.cardinality.metadata.items.items():
                    if metadata_item == "default":
                        has_default = True

                        the_type += " = field(default={})".format(
                            self.__class__._ExpressionToPython(metadata_value.value),  # pylint: disable=protected-access
                        )
                    else:
                        assert False, metadata_item  # pragma: no cover

            if not has_default:
                the_type += " = field(default=None)"

            potential_metadata_item_prefix = "self.{} is not None and ".format(name)

        if element.type.metadata:
            for metadata_item, metadata_value in element.type.metadata.items.items():
                if metadata_item == "values":
                    if not isinstance(metadata_value.value, ListExpression):
                        raise SimpleSchemaException("'values' must be a list.", metadata_value.range)

                    if not metadata_value.value.items:
                        raise SimpleSchemaException("'values' must contain at least one item.", metadata_value.range)

                    if isinstance(metadata_value.value.items[0], IntegerExpression):
                        int_values: Dict[str, int] = {}

                        for item in metadata_value.value.items:
                            if not isinstance(item, IntegerExpression):
                                raise SimpleSchemaException("All items must be integers.", item.range)

                            int_values["Value{}".format(item.value)] = item.value

                        self._includes.setdefault("enum", set()).add("Enum")

                        self._header_stack[-1].write(
                            textwrap.dedent(
                                """\
                                class {}Enum(Enum):
                                {}

                                """,
                            ).format(
                                name,
                                "\n".join("    {} = {}".format(k, v) for k, v in int_values.items()),
                            ),
                        )

                    elif isinstance(metadata_value.value.items[0], StringExpression):
                        string_values: List[str] = []

                        for item in metadata_value.value.items:
                            if not isinstance(item, StringExpression):
                                raise SimpleSchemaException("All items must be strings.", item.range)

                            if not item.value.isalpha():
                                raise SimpleSchemaException("Enum values must be alphabetic strings.", item.range)

                            string_values.append(item.value)

                        self._includes.setdefault("enum", set()).add("auto")
                        self._includes["enum"].add("Enum")

                        self._header_stack[-1].write(
                            textwrap.dedent(
                                """\
                                class {}Enum(Enum):
                                {}

                                """,
                            ).format(
                                name,
                                "\n".join("    {} = auto()".format(v) for v in string_values),
                            ),
                        )

                    elif isinstance(metadata_value.value.items[0], TupleExpression):
                        is_integer: Optional[bool] = None
                        name_prefix = ""

                        tuple_values: Dict[Union[int, str], str] = {}

                        for item in metadata_value.value.items:
                            if (
                                not isinstance(item, TupleExpression)
                                or len(item.expressions) != 2
                            ):
                                raise SimpleSchemaException("All items must be tuples.", item.range)

                            if not isinstance(item.expressions[0], (IntegerExpression, StringExpression)):
                                raise SimpleSchemaException("The 1st tuple element must be an integer or string.", item.expressions[0].range)

                            if is_integer is None:
                                is_integer = isinstance(item.expressions[0], IntegerExpression)
                                name_prefix = "Value"
                            elif (is_integer and not isinstance(item.expressions[0], IntegerExpression)):
                                raise SimpleSchemaException("An integer was expected.", item.expressions[0].range)
                            elif (not is_integer and not isinstance(item.expressions[0], StringExpression)):
                                raise SimpleSchemaException("A string was expected.", item.expressions[0].range)

                            if not isinstance(item.expressions[1], StringExpression):
                                raise SimpleSchemaException("The 2nd tuple element must be a string.", item.expressions[1].range)

                            tuple_values[item.expressions[0].value] = item.expressions[1].value

                        self._includes.setdefault("enum", set()).add("Enum")

                        self._header_stack[-1].write(
                            textwrap.dedent(
                                """\
                                class {}Enum(str, Enum):
                                {}

                                """,
                            ).format(
                                name,
                                "\n".join('    {}{} = "{}"'.format(name_prefix, k, v) for k, v in tuple_values.items()),
                            ),
                        )

                    else:
                        raise SimpleSchemaException("'values' items must be integers, strings, or tuples.", metadata_value.value.items[0].range)

                elif metadata_item == "min":
                    self._post_init_stack[-1].write(
                        textwrap.dedent(
                            """\
                            if {prefix}self.{var} < {val}:
                                raise SimpleSchemaException(
                                    "'{var}' must be greater than or equal to '{val}' ('{{}}' was provided).".format(self.{var}),
                                    self.range,
                                )

                            """,
                        ).format(
                            prefix=potential_metadata_item_prefix,
                            var=name,
                            val=self.__class__._ExpressionToPython(metadata_value.value),  # pylint: disable=protected-access
                        ),
                    )

                elif metadata_item == "max":
                    self._post_init_stack[-1].write(
                        textwrap.dedent(
                            """\
                            if {prefix}self.{var} > {val}:
                                raise SimpleSchemaException(
                                    "'{var}' must be less than or equal to '{val}' ('{{}}' was provided).".format(self.{var}),
                                    self.range,
                                )

                            """,
                        ).format(
                            prefix=potential_metadata_item_prefix,
                            var=name,
                            val=self.__class__._ExpressionToPython(metadata_value.value),  # pylint: disable=protected-access
                        ),
                    )

                else:
                    assert False, metadata_item  # pragma: no cover

        self._stream_stack[-1].write("{}: {}\n".format(name, the_type))

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnExtensionStatement(
        self,
        element: ExtensionStatement,
    ) -> Iterator[Optional[VisitResult]]:
        name = element.name.id.value

        if name != "python_post_init":
            raise SimpleSchemaException("'{}' is not a valid extension name.".format(name), element.name.id.range)

        if (
            element.keyword_args
            or len(element.positional_args) != 1
            or not isinstance(element.positional_args[0], StringExpression)
        ):
            raise SimpleSchemaException(
                "Only one string argument is supported.",
                element.positional_args[0].range,
            )

        self._post_init_stack[-1].write(element.positional_args[0].value)

        yield

    # ----------------------------------------------------------------------
    def __getattr__(
        self,
        name: str,
    ) -> Any:
        match = self.DETAILS_REGEX.match(name)
        if match is not None:
            return self._DefaultDetailsMethod

        # match = self.METHOD_REGEX.match(name)
        # if match is not None:
        #     return self._DefaultMethod

        raise AttributeError(name)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @contextmanager
    def _DefaultMethod(self, *args, **kwargs) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    def _DefaultDetailsMethod(self, *args, **kwargs) -> None:  # pylint: disable=unused-argument
        pass

    # ----------------------------------------------------------------------
    @staticmethod
    def _ExpressionToPython(
        expression: Expression,
    ) -> str:
        if isinstance(expression, BooleanExpression):
            return str(expression.value)
        elif isinstance(expression, IntegerExpression):
            return str(expression.value)
        elif isinstance(expression, NumberExpression):
            return str(expression.value)
        elif isinstance(expression, StringExpression):
            return '"{}"'.format(expression.value.replace('"', '\\"'))
        else:
            assert False, expression  # pragma: no cover


# ----------------------------------------------------------------------
# |
# |  Private Functions
# |
# ----------------------------------------------------------------------
def _GenerateHeader() -> str:
    return textwrap.dedent(
        """\
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        #
        # The file has been automatically generated via ../Build.py using content
        # in ../SimpleSchema.
        #
        # DO NOT MODIFY the contents of this file, as those changes will be
        # overwritten the next time ../Build.py is invoked.
        #
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        """,
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    BuildInfo().Run()
