# ----------------------------------------------------------------------
# |
# |  Build.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-30 07:47:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022-23
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
from dataclasses import dataclass, field
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
    from SimpleSchema.Schema.Elements.Common.Element import Element
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

    from SimpleSchema.Schema.Parse.ANTLR import Parse

    from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseItemStatement import ParseItemStatement
    from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseStructureStatement import ParseStructureStatement
    from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseIdentifierType import ParseIdentifierType

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

                    with init_filename.open("w"):
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
        self._depth_ctr                                 = 0

        self._sink                                      = StringIO()

        self._stack: List[_Visitor._StackFrame]         = []

        self._raw_includes                              = StringIO()
        self._raw_includes_post                         = StringIO()

        # Pre-populate some values to ensure that they appear in the expected order
        self._sorted_includes: Dict[str, Set[str]]      = {
            "dataclasses": set(["dataclass", ]),
            "enum": set(),
            "typing": set(),
            "SimpleSchema.Schema.Elements.Types.FundamentalType": set(["FundamentalType", ]),
        }

    # ----------------------------------------------------------------------
    @property
    def content(self) -> str:
        for include_source, include_items in self._sorted_includes.items():
            if not include_items:
                continue

            include_items = list(include_items)
            include_items.sort()

            self._raw_includes.write(
                "from {} import {}\n".format(include_source, ", ".join(include_items)),
            )

        raw_header_content = self._raw_includes.getvalue()
        raw_header_post_content = self._raw_includes_post.getvalue()

        return textwrap.dedent(
            """\
            {raw_header}{raw_header_post}


            {content}
            """,
        ).format(
            raw_header=raw_header_content.rstrip(),
            raw_header_post="" if not raw_header_post_content else "\n\n{}".format(raw_header_post_content.rstrip()),
            content=self._sink.getvalue().rstrip(),
        )

    # ----------------------------------------------------------------------
    @contextmanager
    def OnElement(self, *args, **kwargs) -> Iterator[Optional[VisitResult]]:
        self._depth_ctr += 1

        # ----------------------------------------------------------------------
        def OnExit():
            assert self._depth_ctr != 0
            self._depth_ctr -= 1

        # ----------------------------------------------------------------------

        with ExitStack(OnExit):
            yield

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
        assert self._depth_ctr > 1, self._depth_ctr

        if self._depth_ctr == 2:
            if element.base is None:
                raise SimpleSchemaException("Structures must have a base.", element.range)

            if not isinstance(element.base, ParseIdentifierType):
                raise SimpleSchemaException("Structures must have an identifier base type.", element.base.range)

            if len(element.base.identifiers) != 1 or element.base.identifiers[0].id.value != "Type":
                raise SimpleSchemaException("The base type for structures must be 'Type'.", element.base.range)

            if not element.cardinality.is_single:
                raise SimpleSchemaException("Structures must be single elements.\n", element.cardinality.range)

            if element.metadata:
                raise SimpleSchemaException("Structures may not have metadata.", element.range)

            name = element.name.id.value

            if name == "Enum":
                self._WriteEnum()

                yield VisitResult.SkipAll
                return

            frame = self.__class__._StackFrame()  # pylint: disable=protected-access

            self._stack.append(frame)
            with ExitStack(self._stack.pop):
                yield

            self._sink.write(
                textwrap.dedent(
                    """\
                    # ----------------------------------------------------------------------
                    @dataclass(frozen=True)
                    class {name}Type(FundamentalType):
                        # ----------------------------------------------------------------------
                        NAME = "{name}"
                    """,
                ).format(name=name),
            )

            indented_stream = StreamDecorator(self._sink, line_prefix="    ")

            # Types
            types_content = frame.types_sink.getvalue()

            if types_content:
                indented_stream.write(
                    textwrap.dedent(
                        """\

                        # ----------------------------------------------------------------------
                        {}
                        """,
                    ).format(types_content.rstrip()),
                )

            # Attributes
            attributes_content = frame.attributes_sink.getvalue()

            if attributes_content:
                indented_stream.write(
                    textwrap.dedent(
                        """\

                        # ----------------------------------------------------------------------
                        {}
                        """,
                    ).format(attributes_content.rstrip()),
                )

            # __post_init__
            post_init_content = frame.post_init_sink.getvalue()

            if post_init_content:
                self._sorted_includes.setdefault("SimpleSchema.Schema.Elements.Common.SimpleSchemaException", set()).add("SimpleSchemaException")

                indented_stream.write(
                    textwrap.dedent(
                        """\

                        # ----------------------------------------------------------------------
                        def __post_init__(self):
                            super({}Type, self).__post_init__(){}
                        """,
                    ).format(
                        name,
                        "" if not post_init_content else
                            TextwrapEx.Indent("\n\n{}".format(post_init_content.rstrip()), 4, skip_first_line=True),
                    ),
                )

            return

        if element.base is not None:
            raise SimpleSchemaException("Nested structures may not have bases.", element.base.range)

        if element.name.id.value != "Python":
            yield VisitResult.SkipAll
            return

        yield

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

        if element.type.cardinality.is_optional:
            self._sorted_includes.setdefault("dataclasses", set()).add("field")

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
                self._sorted_includes.setdefault("typing", set()).add("Optional")
                the_type = "Optional[{}] = field(default=None)".format(the_type)

        if element.type.metadata:
            for metadata_item, metadata_value in element.type.metadata.items.items():
                # We need to process the 'values' metadata item so that we can create the enum type.
                if metadata_item == "values":
                    assert element.type.identifiers[0].id.value == "Enum", element.type.identifiers[0].id.value

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

                        self._sorted_includes.setdefault("enum", set()).add("Enum")

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

                        self._sorted_includes.setdefault("enum", set()).add("auto")
                        self._sorted_includes["enum"].add("Enum")

                        self._stack[-1].types_sink.write(
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

                        self._sorted_includes.setdefault("enum", set()).add("Enum")

                        self._stack[-1].types_sink.write(
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

        self._stack[-1].attributes_sink.write("{}: {}\n".format(name, the_type))

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnExtensionStatement(
        self,
        element: ExtensionStatement,
    ) -> Iterator[Optional[VisitResult]]:
        name = element.name.id.value

        if name in ["header", "header_pre"]:
            sink = self._raw_includes
        elif name == "header_post":
            sink = self._raw_includes_post
        elif name == "post_init":
            sink = self._stack[-1].post_init_sink
        else:
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

        sink.write("{}\n".format(element.positional_args[0].value.rstrip()))

        yield

    # ----------------------------------------------------------------------
    def __getattr__(
        self,
        name: str,
    ) -> Any:
        match = self.DETAILS_REGEX.match(name)
        if match is not None:
            return self._DefaultDetailsMethod

        match = self.METHOD_REGEX.match(name)
        if match is not None:
            return self._DefaultMethod

        raise AttributeError(name)

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class _StackFrame(object):
        types_sink: StringIO                = field(init=False, default_factory=StringIO)
        attributes_sink: StringIO           = field(init=False, default_factory=StringIO)
        post_init_sink: StringIO            = field(init=False, default_factory=StringIO)

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    def _DefaultMethod(self, *args, **kwargs) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    def _DefaultDetailsMethod(
        self,
        element: Union[Element, List[Element]],
        *,
        include_disabled: bool,
    ) -> None:
        if isinstance(element, Element):
            elements = [element]
        else:
            elements = element

        for element in elements:
            if element.is_disabled and not include_disabled:
                continue

            element.Accept(self)

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
    def _WriteEnum(self) -> None:
        self._sorted_includes.setdefault("dataclasses", set()).add("field")

        self._sorted_includes.setdefault("enum", set()).add("Enum")

        self._sorted_includes.setdefault("typing", set()).add("Callable")
        self._sorted_includes["typing"].add("List")
        self._sorted_includes["typing"].add("Tuple")
        self._sorted_includes["typing"].add("Union")
        self._sorted_includes["typing"].add("Type as TypeOf")
        self._sorted_includes["typing"].add("cast")

        self._sorted_includes.setdefault("SimpleSchema.Schema.Elements.Common.SimpleSchemaException", set()).add("SimpleSchemaException")

        self._sink.write(
            textwrap.dedent(
                """\
                # ----------------------------------------------------------------------
                @dataclass(frozen=True)
                class EnumType(FundamentalType):
                    NAME = "Enum"

                    # ----------------------------------------------------------------------
                    _EnumItemType = Union[int, str]

                    values: Union[
                        List[_EnumItemType],
                        List[Tuple[_EnumItemType, str]],
                    ]

                    starting_value: int                 = field(default=0)

                    EnumClass: TypeOf[Enum]             = field(init=False)

                    # ----------------------------------------------------------------------
                    def __post_init__(self):
                        super(EnumType, self).__post_init__()

                        if not self.values:
                            raise SimpleSchemaException("Enum values must be provided.", self.range)

                        if self.starting_value < 0:
                            raise SimpleSchemaException("'starting_value' must be greater than or equal to '0' ('{}' was provided).".format(self.starting_value), self.range)

                        if isinstance(self.values[0], tuple):
                            # ----------------------------------------------------------------------
                            def GetTupleValue(index):
                                v = self.values[index]

                                if not isinstance(v, tuple):
                                    raise SimpleSchemaException("A tuple was expected (index: {}).".format(index), self.range)

                                return v[0]

                            # ----------------------------------------------------------------------
                            def CreateTupleEnumType(
                                value_to_enum_name_func: Callable[[EnumType._EnumItemType], str],
                            ) -> TypeOf[Enum]:
                                return Enum(
                                    "EnumClass",
                                    {
                                        value_to_enum_name_func(value[0]): value[1]
                                        for value in cast(List[Tuple[EnumType._EnumItemType, str]], self.values)
                                    },
                                    type="str",
                                )

                            # ----------------------------------------------------------------------

                            get_value_func = GetTupleValue
                            create_enum_type = CreateTupleEnumType

                        else:
                            # ----------------------------------------------------------------------
                            def GetNonTupleValue(index):
                                v = self.values[index]

                                if isinstance(v, tuple):
                                    raise SimpleSchemaException("A tuple value was not expected (index: {}).".format(index), self.range)

                                return v

                            # ----------------------------------------------------------------------
                            def CreateNonTupleEnumType(
                                value_to_enum_name_func: Callable[[EnumType._EnumItemType], str],
                            ) -> TypeOf[Enum]:
                                import itertools

                                return Enum(
                                    "EnumClass",
                                    {
                                        value_to_enum_name_func(value): int_value
                                        for value, int_value in zip(cast(List[EnumType._EnumItemType], self.values), itertools.count(self.starting_value))
                                    },
                                )

                            # ----------------------------------------------------------------------

                            get_value_func = GetNonTupleValue
                            create_enum_type = CreateNonTupleEnumType

                        if isinstance(get_value_func(0), int):
                            value_to_enum_name_func = lambda value: "Value{}".format(value)  # pylint: disable=unnecessary-lambda

                            for value_index in range(len(self.values)):
                                if not isinstance(get_value_func(value_index), int):
                                    raise SimpleSchemaException("An integer was expected (index: {}).".format(value_index), self.range)

                        elif isinstance(get_value_func(0), str):
                            value_to_enum_name_func = lambda value: value

                            for value_index in range(len(self.values)):
                                if not isinstance(get_value_func(value_index), str):
                                    raise SimpleSchemaException("A string was expected (index: {}).".format(value_index), self.range)

                        else:
                            raise SimpleSchemaException("A string or integer is required.", self.range)

                        object.__setattr__(self, "EnumClass", create_enum_type(value_to_enum_name_func))
                """,
            ),
        )


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
