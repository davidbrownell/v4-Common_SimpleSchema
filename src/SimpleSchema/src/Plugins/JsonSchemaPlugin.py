# ----------------------------------------------------------------------
# |
# |  JsonSchemaPlugin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-05-08 06:45:23
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
from functools import cached_property
from pathlib import Path
from typing import Any, Callable, ClassVar, Iterator, Optional

from Common_Foundation import RegularExpression
from Common_Foundation.Types import overridemethod

from Common_FoundationEx import TyperEx

# ----------------------------------------------------------------------
# pylint: disable=import-error
from SimpleSchema.Common.Range import Range

from SimpleSchema.Plugin import Plugin as PluginBase

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Element import Element
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

from SimpleSchema.Schema.Visitors.Visitor import Visitor, VisitResult


# ----------------------------------------------------------------------
# pylint: disable=invalid-name

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
class Plugin(PluginBase):
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
        return "Generates a JSON Schema (https://json-schema.org)"

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
            "schema_version": TyperEx.TypeDefinitionItem(
                str,
                TyperEx.typer.Option(
                    "https://json-schema.org/draft/2020-12/schema#",
                    "--schema-version",
                    help="JSON Schema version.",
                ),
            ),
            "allow_additional_data": TyperEx.TypeDefinitionItem(
                bool,
                TyperEx.typer.Option(
                    False,
                    "--allow-additional-data",
                    help="If True, unrecognized data in all structures will not cause validation errors.",
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

        visitor = _Visitor(
            self,
            allow_additional_data=command_line_args["allow_additional_data"],
        )

        root.Accept(visitor)

        # Finalize the schema
        for k, v in visitor.schema.items():
            schema[k] = v

        # Write the schema file
        on_status_update_func("Writing schema...")

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

        self._plugin                                    = plugin
        self._allow_additional_data                     = allow_additional_data

        self._schema_stack: list[dict[str, Any]]        = [
            {
                "$defs": {},  # placeholder populated by the schema property
                "type": "object",
                "additionalProperties": self._allow_additional_data,
                "properties": {},
                "required": [],
            },
        ]

        self._definitions: dict[str, Any]               = {}
        self._display_type_as_reference: bool           = False

    # ----------------------------------------------------------------------
    @cached_property
    def schema(self) -> dict[str, Any]:
        assert len(self._schema_stack) == 1, self._schema_stack

        schema = self._schema_stack[0]

        if self._definitions:
            schema["$defs"] = self._definitions
        else:
            del schema["$defs"]

        return schema

    # ----------------------------------------------------------------------
    # |
    # |  Common
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnCardinality(self, element: Cardinality) -> Iterator[Optional[VisitResult]]:
        raise Exception("This should never be called.")  # pragma: no cover

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnMetadata(self, element: Metadata) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        # Metadata is handled inline
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
    def OnItemStatement(self, element: ItemStatement) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield None

        self._schema_stack[-1]["properties"][element.name.value] = self._definitions.pop(element.type.unique_name)

        if element.type.cardinality.min.value != 0:
            self._schema_stack[-1]["required"].append(element.name.value)

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnRootStatement(self, element: RootStatement) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield None

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]: # pylint: disable=unused-argument
        self._schema_stack.append(
            {
                "type": "object",
                "properties" : {},
                "required": [],
            },
        )

        yield

        self._definitions[element.unique_name] = self._schema_stack.pop()

    # ----------------------------------------------------------------------
    # |
    # |  Types
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnBooleanType(self, element: BooleanType) -> Iterator[Optional[VisitResult]]:
        self._definitions[element.unique_name] = {
            "type": "boolean",
        }

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnDateTimeType(self, element: DateTimeType) -> Iterator[Optional[VisitResult]]:
        self._definitions[element.unique_name] = {
            "type": "string",
            "format": "date-time", # ISO 8601
        }

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnDateType(self, element: DateType) -> Iterator[Optional[VisitResult]]:
        self._definitions[element.unique_name] = {
            "type": "string",
            "format": "date", # ISO 8601
        }

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnDirectoryType(self, element: DirectoryType) -> Iterator[Optional[VisitResult]]:
        self._definitions[element.unique_name] = {
            "type": "string",
            "minLength": 1,
            self.__class__.ADDITIONAL_METADATA_ATTRIBUTE_NAME: {
                "ensure_exists": element.ensure_exists,
            },
        }

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnDurationType(self, element: DurationType) -> Iterator[Optional[VisitResult]]:
        self._definitions[element.unique_name] = {
            "type": "string",
            "format": "duration", # RFC 3339
        }

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnFilenameType(self, element: FilenameType) -> Iterator[Optional[VisitResult]]:
        d: dict[str, Any] = {
            "type": "string",
            "minLength": 1,
            self.__class__.ADDITIONAL_METADATA_ATTRIBUTE_NAME: {
                "ensure_exists": element.ensure_exists,
            }
        }

        if element.ensure_exists:
            d[self.__class__.ADDITIONAL_METADATA_ATTRIBUTE_NAME]["match_any"] = element.match_any

        self._definitions[element.unique_name] = d

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnEnumType(self, element: EnumType) -> Iterator[Optional[VisitResult]]:
        self._definitions[element.unique_name] = {
            "type": "string",
            "enum": [e.name for e in element.EnumClass],  # type: ignore
            self.__class__.ADDITIONAL_METADATA_ATTRIBUTE_NAME:  {
                "values": [e.value for e in element.EnumClass],  # type: ignore
            },
        }

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnGuidType(self, element: GuidType) -> Iterator[Optional[VisitResult]]:
        self._definitions[element.unique_name] = {
            "type": "string",
            "format": "uuid", # RFC 4122
        }

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnIntegerType(self, element: IntegerType) -> Iterator[Optional[VisitResult]]:
        d: dict[str, Any] = {
            "type": "integer",
        }

        if element.min is not None:
            d["minimum"] = element.min
        if element.max is not None:
            d["maximum"] = element.max

        if element.bits is not None:
            d[self.__class__.ADDITIONAL_METADATA_ATTRIBUTE_NAME] = {
                "bits": str(element.bits),
            }

        self._definitions[element.unique_name] = d

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnNumberType(self, element: NumberType) -> Iterator[Optional[VisitResult]]:
        d: dict[str, Any] = {
            "type": "number",
        }

        if element.min is not None:
            d["minimum"] = element.min
        if element.max is not None:
            d["maximum"] = element.max

        if element.bits is not None:
            d[self.__class__.ADDITIONAL_METADATA_ATTRIBUTE_NAME] = {
                "bits": str(element.bits),
            }

        self._definitions[element.unique_name] = d

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnReferenceType(self, element: ReferenceType) -> Iterator[Optional[VisitResult]]:
        display_type_as_reference = element.category != ReferenceType.Category.Source
        self._display_type_as_reference = display_type_as_reference

        yield None

        # Get the type
        if element.category == ReferenceType.Category.Source:
            d = self._definitions.pop(element.type.unique_name)
        else:
            d = {
                "$ref": "#/$defs/{}".format(element.type.unique_name),
            }

        if (
            element.category != ReferenceType.Category.Alias
            and element.cardinality.is_container
        ):
            d = {
                "type": "array",
                "items": d,
            }

            if element.cardinality.min.value != 0:
                d["minItems"] = element.cardinality.min.value
            if element.cardinality.max is not None:
                d["maxItems"] = element.cardinality.max.value

        # Process the metadata
        resolved_metadata = element.resolved_metadata

        title = resolved_metadata.get(
            PluralNameMetadataAttribute.name,
            resolved_metadata.get(
                NameMetadataAttribute.name,
                None,
            ),
        )

        if title is not None:
            d["title"] = title.value

        description = resolved_metadata.get(DescriptionMetadataAttribute.name, None)
        if description is not None:
            d["description"] = description.value

        default_value = resolved_metadata.get(DefaultMetadataAttribute.name, None)
        if default_value is not None:
            d["default"] = default_value.value

        # Check if we allow additional data for structures
        if isinstance(element.type, StructureType):
            allow_additional_data = element.resolved_metadata.get(AllowAdditionalDataMetadataAttribute.name, None)
            allow_additional_data = allow_additional_data.value if allow_additional_data is not None else self._allow_additional_data

            d["additionalProperties"] = allow_additional_data

        # Apply the schema
        self._definitions[element.unique_name] = d

    # ----------------------------------------------------------------------
    @overridemethod
    def OnReferenceType__cardinality(
        self,
        element_or_elements: Element.GenerateAcceptDetailsGeneratorItemsType,   # pylint: disable=unused-argument
        *,
        include_disabled: bool,                                                 # pylint: disable=unused-argument
    ) -> Optional[VisitResult]:
        # Handle the cardinality once the ReferenceType has been fully processed
        return None

    # ----------------------------------------------------------------------
    @overridemethod
    def OnReferenceType__type(
        self,
        element_or_elements: Element.GenerateAcceptDetailsGeneratorItemsType,
        *,
        include_disabled: bool,
    ) -> Optional[VisitResult]:
        if self._display_type_as_reference:
            self._display_type_as_reference = False
            return VisitResult.SkipAll

        return self._DefaultDetailMethod("type", element_or_elements, include_disabled=include_disabled)

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnStringType(self, element: StringType) -> Iterator[Optional[VisitResult]]:
        d: dict[str, Any] = {
            "type": "string",
            "minLength": element.min_length,
        }

        if element.max_length is not None:
            d["maxLength"] = element.max_length

        if element.validation_expression is not None:
            # ECMA-262
            d["pattern"] = RegularExpression.PythonToJavaScript(
                element.validation_expression,
            )

        self._definitions[element.unique_name] = d
        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnStructureType(self, element: StructureType) -> Iterator[Optional[VisitResult]]:
        yield None

        self._definitions[element.unique_name] = self._definitions.pop(element.structure.unique_name)

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnTimeType(self, element: TimeType) -> Iterator[Optional[VisitResult]]:
        self._definitions[element.unique_name] = {
            "type": "string",
            "format": "time", # RFC 3339
        }

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnTupleType(self, element: TupleType) -> Iterator[Optional[VisitResult]]:
        yield None

        schemas: list[dict[str, Any]] = []

        for child_type in element.types:
            schemas.append(self._definitions.pop(child_type.unique_name))

        self._definitions[element.unique_name] = {
            "type": "array",
            "items": schemas,
            "minItems": len(element.types),
            "maxItems": len(element.types),
        }

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnUriType(self, element: UriType) -> Iterator[Optional[VisitResult]]:
        self._definitions[element.unique_name] = {
            "type": "string",
            "format": "uri", # RFC 3986
        }

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnVariantType(self, element: VariantType) -> Iterator[Optional[VisitResult]]:
        yield None

        schemas: list[dict[str, Any]] = []

        for child_type in element.types:
            schemas.append(self._definitions.pop(child_type.unique_name))

        self._definitions[element.unique_name] = {
            "oneOf": schemas,
        }
