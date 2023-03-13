# ----------------------------------------------------------------------
# |
# |  JsonSchemaPlugin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-21 08:22:05
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

import json

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, ClassVar, Iterator, Optional, Union

from Common_Foundation import RegularExpression
from Common_Foundation.Types import overridemethod

from Common_FoundationEx import TyperEx


# ----------------------------------------------------------------------
# pylint: disable=import-error
from SimpleSchema.Common.Range import Range

from SimpleSchema.Plugin import Plugin as PluginBase

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Metadata import Metadata, MetadataItem
from SimpleSchema.Schema.Elements.Common.SimpleElement import SimpleElement

from SimpleSchema.Schema.Elements.Expressions.BooleanExpression import BooleanExpression
from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
from SimpleSchema.Schema.Elements.Expressions.ListExpression import ListExpression
from SimpleSchema.Schema.Elements.Expressions.NoneExpression import NoneExpression
from SimpleSchema.Schema.Elements.Expressions.NumberExpression import NumberExpression
from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression
from SimpleSchema.Schema.Elements.Expressions.TupleExpression import TupleExpression

from SimpleSchema.Schema.Elements.Statements.ExtensionStatement import ExtensionStatement, ExtensionStatementKeywordArg
from SimpleSchema.Schema.Elements.Statements.ItemStatement import ItemStatement
from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement
from SimpleSchema.Schema.Elements.Statements.StructureStatement import StructureStatement

from SimpleSchema.Schema.Elements.Types.FundamentalTypes.BooleanType import BooleanType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes.DateTimeType import DateTimeType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes.DateType import DateType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes.DirectoryType import DirectoryType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes.DurationType import DurationType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes.EnumType import EnumType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes.FilenameType import FilenameType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes.GuidType import GuidType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes.IntegerType import IntegerType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes.NumberType import NumberType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes.StringType import StringType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes.TimeType import TimeType
from SimpleSchema.Schema.Elements.Types.FundamentalTypes.UriType import UriType

from SimpleSchema.Schema.Elements.Types.BasicType import BasicType
from SimpleSchema.Schema.Elements.Types.ReferenceType import ReferenceType
from SimpleSchema.Schema.Elements.Types.StructureType import StructureType
from SimpleSchema.Schema.Elements.Types.TupleType import TupleType
from SimpleSchema.Schema.Elements.Types.VariantType import VariantType

from SimpleSchema.Schema.MetadataAttributes.ContainerAttributes import PluralNameMetadataAttribute
from SimpleSchema.Schema.MetadataAttributes.ElementAttributes import DefaultMetadataAttribute, DescriptionMetadataAttribute, NameMetadataAttribute
from SimpleSchema.Schema.MetadataAttributes.MetadataAttribute import MetadataAttribute

from SimpleSchema.Schema.Visitor import Visitor, VisitResult


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class AllowAdditionalDataMetadataAttribute(MetadataAttribute):
    """\
    Attribute that indicates additional data is allowed to be a part of the corresponding structure.

    {
        allow_additional_data: True
    }
    """

    # ----------------------------------------------------------------------
    flags: ClassVar[MetadataAttribute.Flag]             = MetadataAttribute.Flag.Structure
    name: ClassVar[str]                                 = "allow_additional_data"
    type: ClassVar[BasicType]                           = BooleanType(Range.CreateFromCode())


# ----------------------------------------------------------------------
class Plugin(PluginBase):  # pylint: disable=missing-class-docstring

    # ----------------------------------------------------------------------
    # |
    # |  Public Properties
    # |
    # ----------------------------------------------------------------------
    @property
    @overridemethod
    def name(self) -> str:
        return "JsonSchema"

    @property
    @overridemethod
    def description(self) -> str:
        return "Generates a JSON Schema (https://json-schema.org/)."

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(Plugin, self).__init__(
            flags=(
                PluginBase.Flag.AllowRootItems
                | PluginBase.Flag.AllowRootStructures
                | PluginBase.Flag.AllowRootTypes
                | PluginBase.Flag.AllowNestedItems
                | PluginBase.Flag.AllowNestedStructures
                | PluginBase.Flag.AllowNestedTypes
                | PluginBase.Flag.DisableEmptyStructures
                | PluginBase.Flag.FlattenStructureHierarchies
            ),
            custom_extension_names=None,
            custom_metadata_attributes=[
                AllowAdditionalDataMetadataAttribute(),
            ],
        )

    # ----------------------------------------------------------------------
    @overridemethod
    def GetCommandLineArgs(self) -> TyperEx.TypeDefinitionsType:
        return {
            "id": TyperEx.TypeDefinitionItem(
                str,
                TyperEx.typer.Option(
                    "",
                    help="Identifier of the schema.",
                ),
            ),
            "title": TyperEx.TypeDefinitionItem(
                str,
                TyperEx.typer.Option(
                    "",
                    help="Title of the schema.",
                ),
            ),
            "description": TyperEx.TypeDefinitionItem(
                str,
                TyperEx.typer.Option(
                    "",
                    help="Description of the schema.",
                ),
            ),
            "allow_additional_data": TyperEx.TypeDefinitionItem(
                bool,
                TyperEx.typer.Option(
                    False,
                    "--allow-additional-data",
                    help="If True, additional data in any content validation against the generated schema will not cause validation errors.",
                ),
            ),
            "schema_version": TyperEx.TypeDefinitionItem(
                str,
                TyperEx.typer.Option(
                    "https://json-schema.org/draft/2020-12/schema#",
                    "--schema-version",
                    help="JSON Schema version.",
                ),
            ),
        }

    # ----------------------------------------------------------------------
    @overridemethod
    def GetNumAdditionalSteps(
        self,
        context: dict[str, Any],  # pylint: disable=unused-argument
    ) -> int:
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
        return self.__class__._InputFilenameToOutputFilenames(  # pylint: disable=protected-access
            input_root,
            input_filenames,
            output_dir,
            lambda input_filename, default_output_filename: [default_output_filename.with_suffix(".json"), ],
            preserve_dir_structure=preserve_dir_structure,
        )

    # ----------------------------------------------------------------------
    @overridemethod
    def Generate(
        self,
        command_line_args: dict[str, Any],
        root: RootStatement,
        output_filenames: list[Path],
        on_status_update_func: Callable[[str], None],
    ) -> None:
        assert len(output_filenames) == 1
        output_filename = output_filenames[0]
        del output_filenames

        on_status_update_func("Creating schema...")

        # Order is important when defining schema elements
        schema: dict[str, Any] = {}

        for command_line_attribute_name, dest_attribute_name in [
            ("id", "$id"),
            ("schema_version", "$schema"),
            ("title", "title"),
            ("description", "description"),
        ]:
            command_line_value = command_line_args[command_line_attribute_name]
            if not command_line_value:
                continue

            schema[dest_attribute_name] = command_line_value

        schema["$defs"] = {}  # placeholder

        visitor = _Visitor(
            self,
            allow_additional_data=command_line_args["allow_additional_data"],
        )

        root.Accept(visitor)

        # Finalize the schema
        for k, v in visitor.schema.items():
            schema[k] = v

        on_status_update_func("Writing schema...")

        output_filename.parent.mkdir(parents=True, exist_ok=True)

        with output_filename.open("w") as f:
            content = json.dumps(
                schema,
                indent=2,
                separators=(", ", " : "),
            )

            for line in content.splitlines(keepends=False):
                if line.isspace():
                    line = ""

                f.write(line.rstrip())
                f.write("\n")


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _Visitor(Visitor):
    # ----------------------------------------------------------------------
    ADDITIONAL_METADATA_ATTRIBUTE_NAME      = "__custom__"

    # ----------------------------------------------------------------------
    def __init__(
        self,
        plugin: Plugin,
        *,
        allow_additional_data: bool,
    ):
        super(_Visitor, self).__init__()

        self._plugin                                                        = plugin
        self._allow_additional_data                                         = allow_additional_data

        self._schema_stack: list[dict[str, Any]]                            = []
        self._schema: Optional[dict[str, Any]]                              = None

        self._schema_info_lookup: dict[int, _Visitor._SchemaInfo]           = {}

        self._suppress_cardinality: bool                                    = False

    # ----------------------------------------------------------------------
    @property
    def schema(self) -> dict[str, Any]:
        assert not self._schema_stack
        assert self._schema is not None

        return self._schema

    # ----------------------------------------------------------------------
    # |
    # |  Common
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnCardinality(self, element: Cardinality) -> Iterator[Optional[VisitResult]]:
        if self._suppress_cardinality:
            self._suppress_cardinality = False
        elif element.is_container:
            new_schema: dict[str, Any] = {
                "type": "array",
                "items": self._schema_stack.pop(),
            }

            if element.min.value != 0:
                new_schema["minItems"] = element.min.value
            if element.max is not None:
                new_schema["maxItems"] = element.max.value

            self._schema_stack.append(new_schema)

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnMetadata(self, element: Metadata) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnMetadataItem(self, element: MetadataItem) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        raise Exception("This should never be called.")  # pragma: no cover

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnSimpleElement(self, element: SimpleElement) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        # Nothing to do here
        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    # |
    # |  Expressions
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnBooleanExpression(self, element: BooleanExpression) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        raise Exception("This should never be called")  # pragma: no cover

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnIntegerExpression(self, element: IntegerExpression) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        raise Exception("This should never be called")  # pragma: no cover

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnListExpression(self, element: ListExpression) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        raise Exception("This should never be called")  # pragma: no cover

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnNoneExpression(self, element: NoneExpression) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        raise Exception("This should never be called")  # pragma: no cover

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnNumberExpression(self, element: NumberExpression) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        raise Exception("This should never be called")  # pragma: no cover

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnStringExpression(self, element: StringExpression) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        raise Exception("This should never be called")  # pragma: no cover

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnTupleExpression(self, element: TupleExpression) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        raise Exception("This should never be called")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |
    # |  Statements
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnExtensionStatement(self, element: ExtensionStatement) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        raise Exception("This should never be called")  # pragma: no cover

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnExtensionStatementKeywordArg(self, element: ExtensionStatementKeywordArg) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        raise Exception("This should never be called")  # pragma: no cover

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnItemStatement(self, element: ItemStatement) -> Iterator[Optional[VisitResult]]:
        yield

        schema_info_lookup_key = id(element.type)

        schema_info = self._schema_info_lookup[schema_info_lookup_key]

        if (
            isinstance(schema_info.element, ReferenceType)
            and schema_info.element.flags & ReferenceType.Flag.DynamicallyGenerated
        ):
            schema_info = self._schema_info_lookup.pop(schema_info_lookup_key)

        # Process the data generated when the type was visited
        properties = self._schema_stack[-1]["properties"]

        assert element.name.value not in properties, (element.name.value, properties)
        properties[element.name.value] = schema_info.schema

        if not element.type.cardinality.is_optional:
            self._schema_stack[-1]["required"].append(element.name.value)

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnRootStatement(self, element: RootStatement) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        self._schema_stack.append(
            {
                "type": "object",
                "additionalProperties": self._allow_additional_data,
                "properties": {},
                "required": [],
            },
        )

        yield

        self._schema = self._schema_stack.pop()
        assert not self._schema_stack

        self._schema["$defs"] = {
            schema_info.element.unique_name: schema_info.schema
            for schema_info in self._schema_info_lookup.values()
        }

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]:
        schema_info_lookup_key = id(element)

        if schema_info_lookup_key in self._schema_info_lookup:
            yield VisitResult.SkipAll
            return

        self._schema_stack.append(
            {
                "type": "object",
                "additionalProperties": self._allow_additional_data,
                "properties": {},
                "required": [],
            },
        )

        yield

        self._schema_info_lookup[schema_info_lookup_key] = _Visitor._SchemaInfo(
            element,
            self._schema_stack.pop(),
        )

    # ----------------------------------------------------------------------
    # |
    # |  Types
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnBooleanType(self, element: BooleanType) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        d = self._schema_stack[-1]

        d["type"] = "boolean"

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnDateTimeType(self, element: DateTimeType) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        d = self._schema_stack[-1]

        d["type"] = "string"
        d["format"] = "date-time" # ISO 8601

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnDateType(self, element: DateType) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        d = self._schema_stack[-1]

        d["type"] = "string"
        d["format"] = "date" # ISO 8601

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnDirectoryType(self, element: DirectoryType) -> Iterator[Optional[VisitResult]]:
        d = self._schema_stack[-1]

        d["type"] = "string"
        d["minLength"] = 1

        d[self.__class__.ADDITIONAL_METADATA_ATTRIBUTE_NAME] = {
            "ensure_exists": element.ensure_exists,
        }

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnDurationType(self, element: DurationType) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        d = self._schema_stack[-1]

        d["type"] = "string"
        d["format"] = "duration" # RFC 3339

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnFilenameType(self, element: FilenameType) -> Iterator[Optional[VisitResult]]:
        d = self._schema_stack[-1]

        d["type"] = "string"
        d["minLength"] = 1

        d[self.__class__.ADDITIONAL_METADATA_ATTRIBUTE_NAME] = {
            "ensure_exists": element.ensure_exists,
        }

        if element.ensure_exists:
            d[self.__class__.ADDITIONAL_METADATA_ATTRIBUTE_NAME]["match_any"] = element.match_any

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnEnumType(self, element: EnumType) -> Iterator[Optional[VisitResult]]:
        d = self._schema_stack[-1]

        d["type"] = "string"
        d["enum"] = [e.name for e in element.EnumClass]  # type: ignore

        d[self.__class__.ADDITIONAL_METADATA_ATTRIBUTE_NAME] = {
            "values": [e.value for e in element.EnumClass],  # type: ignore
        }

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnGuidType(self, element: GuidType) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        d = self._schema_stack[-1]

        d["type"] = "string"
        d["format"] = "uuid" # RFC 4122

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnIntegerType(self, element: IntegerType) -> Iterator[Optional[VisitResult]]:
        d = self._schema_stack[-1]

        d["type"] = "integer"

        if element.min is not None:
            d["minimum"] = element.min
        if element.max is not None:
            d["maximum"] = element.max

        if element.bits is not None:
            d[self.__class__.ADDITIONAL_METADATA_ATTRIBUTE_NAME] = {
                "bits": str(element.bits),
            }

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnNumberType(self, element: NumberType) -> Iterator[Optional[VisitResult]]:
        d = self._schema_stack[-1]

        d["type"] = "number"

        if element.min is not None:
            d["minimum"] = element.min
        if element.max is not None:
            d["maximum"] = element.max

        if element.bits is not None:
            d[self.__class__.ADDITIONAL_METADATA_ATTRIBUTE_NAME] = {
                "bits": str(element.bits),
            }

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnReferenceType(self, element: ReferenceType) -> Iterator[Optional[VisitResult]]:
        schema_info_lookup_key = id(element)

        if schema_info_lookup_key in self._schema_info_lookup:
            yield VisitResult.SkipAll
            return

        # Prevent infinite recursion by adding an element to the lookup now and populating it later
        self._schema_info_lookup[schema_info_lookup_key] = _Visitor._SchemaInfo(element, {})

        self._schema_stack.append({})

        if (
            not (element.flags & ReferenceType.Flag.BasicRef)
            or (element.flags & ReferenceType.Flag.StructureRef)
        ):
            self._schema_stack[-1]["$ref"] = "#/$defs/{}".format(element.type.unique_name)

        if element.flags & ReferenceType.Flag.Alias:
            self._suppress_cardinality = True

        yield

        new_schema = self._schema_stack.pop()

        resolved_metadata = element.resolved_metadata

        title = resolved_metadata.get(
            PluralNameMetadataAttribute.name,
            resolved_metadata.get(
                NameMetadataAttribute.name,
                None,
            ),
        )

        if title is not None:
            new_schema["title"] = title.value

        description = resolved_metadata.get(DescriptionMetadataAttribute.name, None)
        if description is not None:
            new_schema["description"] = description.value

        default_value = resolved_metadata.get(DefaultMetadataAttribute.name, None)
        if default_value is not None:
            new_schema["default"] = default_value.value

        assert not self._schema_info_lookup[schema_info_lookup_key].schema
        self._schema_info_lookup[schema_info_lookup_key].schema.update(new_schema)

        # Augment the structure definition with the additional data attribute (if necessary)
        if AllowAdditionalDataMetadataAttribute.name in resolved_metadata:
            structure_statement: Optional[StructureStatement] = None

            if element.flags & ReferenceType.Flag.StructureRef:
                assert isinstance(element.type, StructureType)
                structure_statement = element.type.structure
            elif element.flags & ReferenceType.Flag.StructureCollectionRef:
                assert isinstance(element.type, ReferenceType)
                assert isinstance(element.type.type, StructureType)
                structure_statement = element.type.type.structure

            if structure_statement is not None:
                schema_info_lookup_key = id(structure_statement)

                schema_info = self._schema_info_lookup.get(schema_info_lookup_key, None)
                assert schema_info is not None

                schema_info.schema["additionalProperties"] = resolved_metadata[AllowAdditionalDataMetadataAttribute.name].value

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnStringType(self, element: StringType) -> Iterator[Optional[VisitResult]]:
        d = self._schema_stack[-1]

        d["type"] = "string"
        d["minLength"] = element.min_length

        if element.max_length is not None:
            d["maxLength"] = element.max_length

        if element.validation_expression is not None:
            # ECMA-262
            d["pattern"] = RegularExpression.PythonToJavaScript(
                element.validation_expression,
            )

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnStructureType(self, element: StructureType) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield


    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnTimeType(self, element: TimeType) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        d = self._schema_stack[-1]

        d["type"] = "string"
        d["format"] = "time" # RFC 3339

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnTupleType(self, element: TupleType) -> Iterator[Optional[VisitResult]]:
        yield

        schemas: list[dict[str, Any]] = []

        for child_type in element.types:
            schema_info = self._schema_info_lookup.pop(id(child_type))
            schemas.append(schema_info.schema)

        d = self._schema_stack[-1]

        d["type"] = "array"
        d["items"] = schemas
        d["minItems"] = len(element.types)
        d["maxItems"] = len(element.types)

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnUriType(self, element: UriType) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        d = self._schema_stack[-1]

        d["type"] = "string"
        d["format"] = "uri" # RFC 3986

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnVariantType(self, element: VariantType) -> Iterator[Optional[VisitResult]]:
        yield

        schemas: list[dict[str, Any]] = []

        for child_type in element.types:
            schema_info = self._schema_info_lookup.pop(id(child_type))
            schemas.append(schema_info.schema)

        d = self._schema_stack[-1]

        d["oneOf"] = schemas

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class _SchemaInfo(object):
        element: Union[BasicType, ReferenceType, StructureStatement]
        schema: dict[str, Any]
