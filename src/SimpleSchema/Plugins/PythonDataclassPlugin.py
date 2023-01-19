# ----------------------------------------------------------------------
# |
# |  PythonDataclassPlugin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-14 00:07:29
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Plugin object"""

import re
import textwrap

from contextlib import contextmanager
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Any, Callable, cast, Dict, Generator, Iterator, Optional, Tuple, Union

from Common_Foundation.Streams.DoneManager import DoneManager
from Common_Foundation.Streams.StreamDecorator import StreamDecorator
from Common_Foundation import TextwrapEx
from Common_Foundation.Types import overridemethod

from Common_FoundationEx.CompilerImpl.Mixins.OutputProcessorMixins.MultipleOutputProcessorMixin import MultipleOutputProcessorMixin
from Common_FoundationEx.InflectEx import inflect

from SimpleSchema.Plugin import Plugin as PluginBase, VisitResult

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Element import Element, SimpleElement
from SimpleSchema.Schema.Elements.Common.Range import Range
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Statements.ItemStatement import ItemStatement
from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement
from SimpleSchema.Schema.Elements.Statements.Statement import Statement
from SimpleSchema.Schema.Elements.Statements.StructureStatement import StructureStatement

from SimpleSchema.Schema.Elements.Types.AliasType import AliasType
from SimpleSchema.Schema.Elements.Types.FundamentalType import FundamentalType
from SimpleSchema.Schema.Elements.Types import FundamentalTypes
from SimpleSchema.Schema.Elements.Types.StructureType import StructureType
from SimpleSchema.Schema.Elements.Types.TupleType import TupleType
from SimpleSchema.Schema.Elements.Types.Type import Type
from SimpleSchema.Schema.Elements.Types.VariantType import VariantType

from SimpleSchema.Schema.MetadataAttributes.MetadataAttribute import MetadataAttribute


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _MetadataAttributeBase(MetadataAttribute):
    # ----------------------------------------------------------------------
    @overridemethod
    def Validate(
        self,
        element: Element,
    ) -> None:
        if not (
            isinstance(element, StructureStatement)
            and element.name.id.value == "__Python__"
        ):
            raise SimpleSchemaException(
                "The attribute '{}' is not valid in this context.".format(self.name),
                element.range,
            )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ImportStatementsMetadataAttribute(_MetadataAttributeBase):
    """\
    Attribute for custom import statements.

    {
        import_statements: [
            "from foo import Bar",
            "import re",
        ]
    }
    """

    # ----------------------------------------------------------------------
    NAME                                    = "import_statements"

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls) -> "ImportStatementsMetadataAttribute":
        return cls(
            MetadataAttribute.Flag.Structure,
            cls.NAME,
            FundamentalTypes.StringType.Create(
                Range.CreateFromCode(),
                Cardinality.CreateFromCode(1),
                None,
                1,
                None,
                "(?:from .+ )?import .+",
            ),
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class CustomAttributesMetadataAttribute(_MetadataAttributeBase):
    """\
    Attribute for custom python attributes.

    {
        custom_attributes: [
            "value1: str",
            "value2: bool = field(kw_init=True)",
        ]
    }
    """

    # ----------------------------------------------------------------------
    NAME                                    = "custom_attributes"

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls) -> "CustomAttributesMetadataAttribute":
        return cls(
            MetadataAttribute.Flag.Structure,
            cls.NAME,
                FundamentalTypes.StringType.Create(
                Range.CreateFromCode(),
                Cardinality.CreateFromCode(1),
                None,
            ),
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class PythonBaseClassesMetadataAttribute(_MetadataAttributeBase):
    """\
    Base classes for the created class.

    {
        base_classes: ["Base1", "Base2"]
    }
    """

    # ----------------------------------------------------------------------
    NAME                                    = "base_classes"

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls) -> "PythonBaseClassesMetadataAttribute":
        return cls(
            MetadataAttribute.Flag.Structure,
            cls.NAME,
            FundamentalTypes.StringType.Create(
                Range.CreateFromCode(),
                Cardinality.CreateFromCode(1),
                None,
            ),
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class PostInitContentMetadataAttribute(_MetadataAttributeBase):
    '''\
    Custom post init content.

    {
        "post_init_content": """
                             More __post_init__ content here
                             """
    }
    '''

    # ----------------------------------------------------------------------
    NAME                                    = "post_init_content"

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls) -> "PostInitContentMetadataAttribute":
        return cls(
            MetadataAttribute.Flag.Structure,
            cls.NAME,
            FundamentalTypes.StringType.Create(
                Range.CreateFromCode(),
                Cardinality.CreateFromCode(),
                None,
            ),
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class CustomMethodsMetadataAttribute(_MetadataAttributeBase):
    '''\
    Base classes for the created class.

    {
        custom_methods: [
            """
            def Method1(self):
                ...
            """,
            """
            def Method2(self):
                ...
            """,
        ]
    }
    '''

    # ----------------------------------------------------------------------
    NAME                                    = "custom_methods"

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls) -> "CustomMethodsMetadataAttribute":
        return cls(
            MetadataAttribute.Flag.Structure,
            cls.NAME,
            FundamentalTypes.StringType.Create(
                Range.CreateFromCode(),
                Cardinality.CreateFromCode(1),
                None,
            ),
        )


# ----------------------------------------------------------------------
class Plugin(PluginBase):
    # ----------------------------------------------------------------------
    # |
    # |  Public Properties
    # |
    # ----------------------------------------------------------------------
    @property
    @overridemethod
    def name(self) -> str:
        return "python_dataclass"

    @property
    @overridemethod
    def description(self) -> str:
        return "Generates Python dataclass objects."""

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(Plugin, self).__init__(
            flags=(
                PluginBase.Flag.AllowRootStructures
                | PluginBase.Flag.AllowNestedItems
                | PluginBase.Flag.AllowNestedStructures
            ),
            custom_extension_names=None,
            custom_metadata_attributes=[
                ImportStatementsMetadataAttribute.Create(),
                PythonBaseClassesMetadataAttribute.Create(),
                CustomAttributesMetadataAttribute.Create(),
                PostInitContentMetadataAttribute.Create(),
                CustomMethodsMetadataAttribute.Create(),
            ],
        )

        self._import_statement_regex        = re.compile(
            r"""(?#
            Beginning of line               )^(?#
            from statement [begin]          )(?:(?#
                'from'                      )from\s+(?#
                <module_path>               )(?P<module_path>.+?)(?#
                trailing whitespace         )\s+(?#
            from statement [end]            ))?(?#
            'import'                        )import\s+(?#
            <import_content>                )(?P<import_content>.+?)(?#
            End of line                     )$(?#
            )""",
        )

    # ----------------------------------------------------------------------
    @overridemethod
    def ValidateEnvironment(self) -> Optional[str]:
        """\
        Opportunity to valid that a plugin can be run in the current environment.
        """

        # Do nothing by default
        return None

    # ----------------------------------------------------------------------
    @overridemethod
    def GetNumAdditionalSteps(
        self,
        context: Dict[str, Any],  # pylint: disable=unused-argument
    ) -> int:
        """Returns the number of steps required to generate the content."""

        return 0

    # ----------------------------------------------------------------------
    @overridemethod
    def GenerateOutputFilenames(
        self,
        input_root: Path,
        input_filenames: list[Path],
        output_dir: Path,
        *,
        preserve_dir_structure: bool,
    ) -> dict[Path, list[Path]]:
        return self._InputFilenameToOutputFilenames(
            input_root,
            input_filenames,
            output_dir,
            lambda input_filename, default_output_filename: [default_output_filename.with_suffix(".py"), ],
            preserve_dir_structure=preserve_dir_structure,
        )

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnStructureStatement(
        self,
        structure: StructureStatement,
    ) -> Iterator[Optional[VisitResult]]:
        if structure.name.id.value.startswith("__") or structure.name.id.value.endswith("__"):
            name = structure.name.id.value

            if name.startswith("__"):
                name = name[2:]
            if name.endswith("__"):
                name = name[:-2]

            if name != "Python":
                structure.Disable()

                yield
                return

            if structure.children:
                raise SimpleSchemaException("No children were expected.", structure.range)

            import_statements: Optional[SimpleElement] = structure.resolved_metadata.pop(ImportStatementsMetadataAttribute.NAME, None)  # type: ignore

            if import_statements:
                root = self.__class__._GetInitializedRoot(structure)  # pylint: disable=protected-access

                for import_statement in import_statements.value:
                    match = self._import_statement_regex.match(import_statement)
                    if not match:
                        raise SimpleSchemaException(
                            "The import statement did not match the expected format.",
                            import_statement.range,
                        )

                    module_path = match.group("module_path")

                    if not module_path:
                        module_path = None
                    else:
                        module_path = module_path.split(".")

                    self.__class__._AddImport(  # pylint: disable=protected-access
                        root,
                        module_path,
                        [item.strip() for item in match.group("import_content").split(",")],
                    )

            # Get rid of the SimpleElements
            for key, value in list(structure.resolved_metadata.items()):  # type: ignore
                structure.resolved_metadata[key] = value.value  # type: ignore

            structure.Disable()

        yield

    # ----------------------------------------------------------------------
    @overridemethod
    def Generate(
        self,
        output_filenames: list[Path],
        root: RootStatement,
        on_status_update_func: Callable[[str], None],
    ) -> None:
        assert len(output_filenames) == 1
        output_filename = output_filenames[0]
        del output_filenames

        root = self.__class__._GetInitializedRoot(root)  # pylint: disable=protected-access

        # Generate the content
        sink = StringIO()

        for statement in root.statements:
            if statement.is_disabled:
                continue

            if isinstance(statement, StructureStatement):
                self.__class__._OutputStructure(root, sink, statement)  # pylint: disable=protected-access
            else:
                assert False, statement  # pragma: no cover

        # Trim whitespace
        lines: list[str] = sink.getvalue().split("\n")

        for line_index, line in enumerate(lines):
            if line.isspace():
                lines[line_index] = ""

        content = "{}\n".format("\n".join(lines).rstrip())

        # Write to the file
        output_filename.parent.mkdir(parents=True, exist_ok=True)

        with output_filename.open("w") as f:
            f.write(
                self._GenerateFileHeader(
                    line_prefix="# ",
                ),
            )

            f.write(
                textwrap.dedent(
                    """\
                    # pylint: disable=consider-using-f-string
                    # pylint: disable=missing-module-docstring
                    # pylint: disable=missing-class-docstring

                    """,
                ),
            )

            # Imports
            for statement in root.imports.GenerateImportStatements(is_root=True):  # type: ignore
                f.write(statement)
                f.write("\n")

            f.write("\n\n")

            f.write(content)

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class _ImportNode(object):

        # ----------------------------------------------------------------------
        nodes: dict[str, "Plugin._ImportNode"]          = field(init=False, default_factory=dict)
        items: set[str]                                 = field(init=False, default_factory=set)

        # ----------------------------------------------------------------------
        def GenerateImportStatements(
            self,
            *,
            is_root: bool,
        ) -> Generator[str, None, None]:

            if is_root:
                prefix = ""
            else:
                prefix = " "

            if self.items:
                yield "{}import {}".format(prefix, ", ".join(sorted(self.items)))

            if is_root:
                prefix = "from "
            else:
                prefix = "."

            keys = list(self.nodes.keys())

            keys.sort(
                key=lambda value: (
                    0 if value[0].islower() else 1,
                    value.lower(),
                ),
            )

            for key in keys:
                value = self.nodes[key]

                for statement in value.GenerateImportStatements(is_root=False):
                    yield "{prefix}{key}{statement}".format(
                        prefix=prefix,
                        key=key,
                        statement=statement,
                    )

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class _StructureData(object):
        types: list[str]                    = field(init=False, default_factory=list)
        attributes: list[str]               = field(init=False, default_factory=list)
        post_init_stream: StringIO          = field(init=False, default_factory=StringIO)

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def _GetInitializedRoot(
        cls,
        element: Element,
    ) -> RootStatement:
        while not isinstance(element, RootStatement):
            assert element is not None
            element = element.parent

        if not hasattr(element, "imports"):
            object.__setattr__(element, "imports", Plugin._ImportNode())

            cls._AddImport(element, ["dataclasses"], "dataclass")

        return element

    # ----------------------------------------------------------------------
    @staticmethod
    def _AddImport(
        root: RootStatement,
        import_module_path: Optional[list[str]],
        import_item_or_items: Union[str, list[str]],
    ) -> None:
        node: Plugin._ImportNode = root.imports  # type: ignore

        for module_path in (import_module_path or []):
            new_node = node.nodes.get(module_path, None)

            if new_node is None:
                new_node = Plugin._ImportNode()

                node.nodes[module_path] = new_node

            node = new_node

        if isinstance(import_item_or_items, list):
            import_items = import_item_or_items
        else:
            import_items = [import_item_or_items, ]

        for import_item in import_items:
            node.items.add(import_item)

    # ----------------------------------------------------------------------
    @classmethod
    def _OutputStructure(
        cls,
        root: RootStatement,
        stream,
        statement: StructureStatement,
    ) -> None:
        resolved_metadata: dict[str, Any] = next(
            (
                child.resolved_metadata  # type: ignore
                for child in statement.children
                if (isinstance(child, StructureStatement) and child.name.id.value == "__Python__")
            ),
            {},
        )

        structure_data = Plugin._StructureData()

        # Process the children
        for child in statement.children:
            if child.is_disabled:
                continue

            if isinstance(child, ItemStatement):
                cls._OutputItem(root, structure_data, child)

            elif isinstance(child, StructureStatement):
                sink = StringIO()

                cls._OutputStructure(root, sink, child)

                structure_data.types.append(sink.getvalue())

            else:
                assert False, child  # pragma: no cover

        # Create the class
        bases = resolved_metadata.get(PythonBaseClassesMetadataAttribute.NAME, None)

        stream.write(
            textwrap.dedent(
                """\
                # ----------------------------------------------------------------------
                @dataclass(frozen=True)
                class {name}({bases}):
                """,
            ).format(
                name=statement.name.id.value,
                bases=", ".join(bases or ["object", ]),
            ),
        )

        indented_stream = StreamDecorator(stream, "    ")

        # Types
        if structure_data.types:
            indented_stream.write(
                textwrap.dedent(
                    """\
                    # ----------------------------------------------------------------------
                    # |  Types
                    {}

                    """,
                ).format(
                    "".join(
                        textwrap.dedent(
                            """\
                            {}

                            """,
                        ).format(type_def.rstrip())
                        for type_def in structure_data.types
                    ).rstrip(),
                ),
            )

        # Attributes
        custom_attributes: Optional[list[str]] = resolved_metadata.get(CustomAttributesMetadataAttribute.NAME, None)

        if structure_data.attributes or custom_attributes:
            indented_stream.write(
                textwrap.dedent(
                    """\
                    # ----------------------------------------------------------------------
                    # |  Attributes
                    # ----------------------------------------------------------------------
                    """,
                ),
            )

            if structure_data.attributes:
                indented_stream.write("\n".join(structure_data.attributes).rstrip())
                indented_stream.write("\n\n")

            if custom_attributes:
                indented_stream.write("\n".join(custom_attributes).rstrip())
                indented_stream.write("\n\n")

        # Methods
        indented_stream.write(
            textwrap.dedent(
                """\
                # ----------------------------------------------------------------------
                # |  Methods
                """,
            ),
        )

        # __post_init__
        indented_stream.write(
            textwrap.dedent(
                """\
                # ----------------------------------------------------------------------
                def __post_init__(self):
                """,
            ),
        )

        post_init_stream = StreamDecorator(indented_stream, "    ")
        wrote_to_post_init_stream = False

        if bases:
            post_init_stream.write("\n".join("{}.__post_init__(self)".format(base) for base in bases))
            post_init_stream.write("\n\n")

            wrote_to_post_init_stream = True

        post_init_content = structure_data.post_init_stream.getvalue()
        if post_init_content:
            post_init_stream.write(post_init_content.rstrip())
            post_init_stream.write("\n\n")

            wrote_to_post_init_stream = True

        post_init_content = resolved_metadata.get(PostInitContentMetadataAttribute.NAME, None)
        if post_init_content is not None:
            post_init_stream.write(post_init_content.rstrip())
            post_init_stream.write("\n\n")

            wrote_to_post_init_stream = True

        if not wrote_to_post_init_stream:
            post_init_stream.write("pass\n\n")

        # Custom methods
        custom_methods: Optional[list[str]] = resolved_metadata.get(CustomMethodsMetadataAttribute.NAME, None)

        if custom_methods:
            indented_stream.write(
                "".join(
                    textwrap.dedent(
                        """\
                        {}{}

                        """,
                    ).format(
                        "" if custom_method.startswith("# -----") else "# ----------------------------------------------------------------------\n",
                        custom_method.rstrip(),
                    )
                    for custom_method in custom_methods
                ).rstrip(),
            )

        indented_stream.flush()

    # ----------------------------------------------------------------------
    @classmethod
    def _OutputItem(
        cls,
        root: RootStatement,
        structure_data: _StructureData,
        statement: ItemStatement,
    ) -> None:

        var_name = "self.{}".format(statement.name.id.value)

        post_init_stream = StringIO()

        if statement.type.cardinality.is_container:
            if statement.type.cardinality.min.value != 0 or statement.type.cardinality.max is not None:
                post_init_stream.write(
                    textwrap.dedent(
                        """\
                        num_items = len({})

                        """,
                    ).format(var_name),
                )

                if statement.type.cardinality.min.value != 0:
                    post_init_stream.write(
                        textwrap.dedent(
                            """\
                            if num_items < {value}:
                                if num_items == 1:
                                    item_plural = "item"
                                    was_plural = "was"
                                else:
                                    item_plural = "items"
                                    was_plural = "were"

                                raise Exception("At least {expected} {expected_verb} expected ({{}} {{}} {{}} found).".format(num_items, item_plural, was_plural))

                            """,
                        ).format(
                            value=statement.type.cardinality.min.value,
                            expected=inflect.no("item", statement.type.cardinality.min.value),
                            expected_verb=inflect.plural_verb("was", statement.type.cardinality.min.value),
                        ),
                    )

                if statement.type.cardinality.max is not None:
                    post_init_stream.write(
                        textwrap.dedent(
                            """\
                            if num_items > {value}:
                                if num_items == 1:
                                    item_plural = "item"
                                    was_plural = "was"
                                else:
                                    item_plural = "items"
                                    was_plural = "were"

                                raise Exception("Only {expected} {expected_verb} expected ({{}} {{}} {{}} found).".format(num_items, item_plural, was_plural))

                            """,
                        ).format(
                            value=statement.type.cardinality.max.value,
                            expected=inflect.no("item", statement.type.cardinality.max.value),
                            expected_verb=inflect.plural_verb("was", statement.type.cardinality.max.value),
                        ),
                    )

            item_post_init_stream = StringIO()

            the_type = cls._TypeToPythonType(
                root,
                statement.name.id.value,
                statement.type,
                "item",
                item_post_init_stream,
                structure_data.types,
            )

            item_post_init_stream = item_post_init_stream.getvalue()
            if item_post_init_stream:
                post_init_stream.write(
                    textwrap.dedent(
                        """\
                        for item in {}:
                            {}

                        """,
                    ).format(
                        var_name,
                        TextwrapEx.Indent(item_post_init_stream.rstrip(), 4, skip_first_line=True),
                    ),
                )

            the_type = "list[{}]".format(the_type)

        else:
            item_post_init_stream = StringIO()

            the_type = cls._TypeToPythonType(
                root,
                statement.name.id.value,
                statement.type,
                var_name,
                item_post_init_stream,
                structure_data.types,
            )

            item_post_init_stream = item_post_init_stream.getvalue()

            if statement.type.cardinality.is_optional:
                cls._AddImport(root, ["dataclasses", ], "field")

                has_default = False

                if statement.type.cardinality.metadata is not None:
                    for metadata_value in statement.type.cardinality.metadata.items.values():
                        if metadata_value.is_disabled:
                            continue

                        if metadata_value.name.id.value == "default":
                            has_default = True

                            the_type += " = field(default={})".format(
                                statement.type.ParseExpression(metadata_value.value),
                            )

                            continue

                        raise SimpleSchemaException(
                            "The metadata value '{}' was not expected.".format(metadata_value.name.id.value),
                            metadata_value.range,
                        )

                if not has_default:
                    cls._AddImport(root, ["typing", ], "Optional")

                    the_type = "Optional[{}] = field(default=None)".format(the_type)

                    if item_post_init_stream:
                        item_post_init_stream = textwrap.dedent(
                            """\
                            if {} is not None:
                                {}

                            """,
                        ).format(
                            var_name,
                            TextwrapEx.Indent(item_post_init_stream.rstrip(), 4, skip_first_line=True),
                        )

            if item_post_init_stream:
                post_init_stream.write(item_post_init_stream)

        post_init_stream = post_init_stream.getvalue()
        if post_init_stream:
            structure_data.post_init_stream.write(
                textwrap.dedent(
                    """\
                    # {}
                    {}

                    """,
                ).format(var_name, post_init_stream.rstrip()),
            )

        structure_data.attributes.append("{}: {}".format(statement.name.id.value, the_type))

    # ----------------------------------------------------------------------
    @classmethod
    def _TypeToPythonType(
        cls,
        root: RootStatement,
        original_name: str,
        the_type: Type,
        var_name: str,
        post_init_stream: StringIO,
        structure_types: list[str],
    ) -> str:
        if isinstance(the_type, AliasType):
            raise SimpleSchemaException("Alias types cannot be represented as python types.", the_type.range)

        if isinstance(the_type, FundamentalType):
            if isinstance(the_type, FundamentalTypes.BooleanType):
                return "bool"

            if isinstance(the_type, FundamentalTypes.DateType):
                cls._AddImport(root, ["datetime", ], "date")
                return "date"

            if isinstance(the_type, FundamentalTypes.DateTimeType):
                cls._AddImport(root, ["datetime", ], "datetime")
                return "datetime"

            if isinstance(the_type, FundamentalTypes.DirectoryType):
                cls._AddImport(root, ["pathlib", ], "Path")

                if the_type.constraint.ensure_exists:
                    post_init_stream.write(
                        textwrap.dedent(
                            """\
                            if not {var_name}.is_dir():
                                raise Exception("'{{}}' is not a valid directory.".format({var_name}))
                            """,
                        ).format(
                            var_name=var_name,
                        ),
                    )

                return "Path"

            if isinstance(the_type, FundamentalTypes.DurationType):
                cls._AddImport(root, ["datetime", ], "timedelta")
                return "timedelta"

            if isinstance(the_type, FundamentalTypes.EnumType):
                cls._AddImport(root, ["enum"], "Enum")

                class_name = "{}Enum".format(original_name)

                if isinstance(the_type.values[0], tuple):
                    is_str = True
                    decorate_value_func = lambda value: '"{}"'.format(value)
                else:
                    is_str = False
                    decorate_value_func = lambda value: value

                structure_types.append(
                    textwrap.dedent(
                        """\
                        # ----------------------------------------------------------------------
                        class {name}({str_base}Enum):
                            {statements}

                        """,
                    ).format(
                        name=class_name,
                        str_base="str, " if is_str else "",
                        statements=TextwrapEx.Indent(
                            "\n".join(
                                "{} = {}".format(e.name, decorate_value_func(e.value))
                                for e in the_type.EnumClass
                            ),
                            4,
                            skip_first_line=True,
                        ),
                    ),
                )

                return class_name

            if isinstance(the_type, FundamentalTypes.FilenameType):
                cls._AddImport(root, ["pathlib", ], "Path")

                if the_type.constraint.ensure_exists:
                    if the_type.constraint.match_any:
                        suffix = "exists"
                        desc = "filename or directory"
                    else:
                        suffix = "is_file"
                        desc = "filename"

                    post_init_stream.write(
                        textwrap.dedent(
                            """\
                            if not {var_name}.{suffix}():
                                raise Exception("'{{}}' is not a valid {desc}.".format({var_name}))
                            """,
                        ).format(
                            var_name=var_name,
                            suffix=suffix,
                            desc=desc,
                        ),
                    )

            if isinstance(the_type, FundamentalTypes.GuidType):
                cls._AddImport(root, ["uuid", ], "UUID")
                return "UUID"

            if isinstance(the_type, FundamentalTypes.IntegerType):
                if the_type.constraint.min is not None:
                    post_init_stream.write(
                        textwrap.dedent(
                            """\
                            if {var_name} < {min_value}:
                                raise Exception("Value must be >= {min_value} ({{}} was found).".format({var_name}))
                            """,
                        ).format(
                            var_name=var_name,
                            min_value=the_type.constraint.min,
                        ),
                    )

                if the_type.constraint.max is not None:
                    post_init_stream.write(
                        textwrap.dedent(
                            """\
                            if {var_name} > {max_value}:
                                raise Exception("Value must be <= {max_value} ({{}} was found).".format({var_name}))
                            """,
                        ).format(
                            var_name=var_name,
                            max_value=the_type.constraint.max,
                        ),
                    )

                return "int"

            if isinstance(the_type, FundamentalTypes.NumberType):
                if the_type.constraint.min is not None:
                    post_init_stream.write(
                        textwrap.dedent(
                            """\
                            if {var_name} < {min_value}:
                                raise Exception("Value must be >= {min_value} ({{}} was found).".format({var_name}))
                            """,
                        ).format(
                            var_name=var_name,
                            min_value=the_type.constraint.min,
                        ),
                    )

                if the_type.constraint.max is not None:
                    post_init_stream.write(
                        textwrap.dedent(
                            """\
                            if {var_name} > {max_value}:
                                raise Exception("Value must be <= {max_value} ({{}} was found).".format({var_name}))
                            """,
                        ).format(
                            var_name=var_name,
                            max_value=the_type.constraint.max,
                        ),
                    )

                return "float"

            if isinstance(the_type, FundamentalTypes.StringType):
                post_init_stream.write(
                    textwrap.dedent(
                        """\
                        num_chars = len({var_name})

                        if num_chars < {value}:
                            if num_chars == 1:
                                char_plural = "character"
                                was_plural = "was"
                            else:
                                char_plural = "characters"
                                was_plural = "were"

                            raise Exception("At least {expected} {expected_verb} expected ({{}} {{}} {{}} found).".format(num_chars, char_plural, was_plural))

                        """,
                    ).format(
                        var_name=var_name,
                        value=the_type.constraint.min_length,
                        expected=inflect.no("character", the_type.constraint.min_length),
                        expected_verb=inflect.plural_verb("was", the_type.constraint.min_length),
                    ),
                )

                if the_type.constraint.max_length is not None:
                    post_init_stream.write(
                        textwrap.dedent(
                            """\
                            if num_chars > {value}:
                                if num_chars == 1:
                                    char_plural = "character"
                                    was_plural = "was"
                                else:
                                    char_plural = "characters"
                                    was_plural = "were"

                                raise Exception("Only {expected} {expected_verb} expected ({{}} {{}} {{}} found).".format(num_chars, char_plural, was_plural))

                            """,
                        ).format(
                            var_name=var_name,
                            value=the_type.constraint.max_length,
                            expected=inflect.no("character", the_type.constraint.max_length),
                            expected_verb=inflect.plural_verb("was", the_type.constraint.max_length),
                        ),
                    )

                if the_type.constraint.validation_regex is not None:
                    cls._AddImport(root, None, "re")

                    post_init_stream.write(
                        textwrap.dedent(
                            """\
                            if not re.match(r"{expr}", {var_name}):
                                raise Exception(r"The string '{{}}' does not match the regular expression '{expr}'.".format({var_name}))

                            """,
                        ).format(
                            var_name=var_name,
                            expr=the_type.constraint.validation_regex.pattern,
                        ),
                    )

                return "str"

            if isinstance(the_type, FundamentalTypes.TimeType):
                cls._AddImport(root, ["datetime", ], "time")
                return "time"

            if isinstance(the_type, FundamentalTypes.UriType):
                return "str"

            assert False, the_type  # pragma: no cover

        if isinstance(the_type, StructureType):
            return the_type.statement.name.id.value

        if isinstance(the_type, TupleType):
            cls._AddImport(root, ["typing", ], "Tuple")

            post_init_stream.write(
                textwrap.dedent(
                    """\
                    num_elements = len({var_name})

                    if num_elements != {num_elements}:
                        if num_elements == 1:
                            element_plural = "element"
                            was_plural = "was"
                        else:
                            element_plural = "elements"
                            was_plural = "were"

                        raise Exception("{expected} {expected_verb} expected ({{}} {{}} {{}} found).".format(num_elements, element_plural, was_plural))

                    """,
                ).format(
                    var_name=var_name,
                    num_elements=len(the_type.types),
                    expected=inflect.no("tuple element", len(the_type.types)),
                    expected_verb=inflect.plural_verb("was", len(the_type.types)),
                ),
            )

            type_names: list[str] = []

            for child_type_index, child_type in enumerate(the_type.types):
                tuple_item_post_init_stream = StringIO()

                type_names.append(
                    cls._TypeToPythonType(
                        root,
                        "{}{}".format(original_name, child_type_index),
                        child_type,
                        "{}[{}]".format(var_name, child_type_index),
                        tuple_item_post_init_stream,
                        structure_types,
                    ),
                )

                tuple_item_post_init_stream = tuple_item_post_init_stream.getvalue()
                if tuple_item_post_init_stream:
                    post_init_stream.write(
                        textwrap.dedent(
                            """\
                            # {} - Element {}
                            {}

                            """,
                        ).format(
                            var_name,
                            child_type_index,
                            tuple_item_post_init_stream.rstrip(),
                        ),
                    )

            return "Tuple[{}]".format(", ".join(type_names))

        if isinstance(the_type, VariantType):
            return "BugBug (variant)"

        assert False, the_type  # pragma: no cover
