# ----------------------------------------------------------------------
# |
# |  DiagnosticPlugin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-08 11:27:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Diagnostic plugin object"""

from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Iterator, Optional

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation.Types import EnsureValid, overridemethod

from Common_FoundationEx import TyperEx


# ----------------------------------------------------------------------
# pylint: disable=import-error
from SimpleSchema.Common.Range import Range
from SimpleSchema.Common.SafeYaml import ToYamlString

from SimpleSchema.Plugin import Plugin as PluginBase

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.Metadata import Metadata, MetadataItem
from SimpleSchema.Schema.Elements.Common.SimpleElement import SimpleElement
from SimpleSchema.Schema.Elements.Common.UniqueNameTrait import UniqueNameTrait

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

from SimpleSchema.Schema.Elements.Types.ReferenceType import ReferenceType
from SimpleSchema.Schema.Elements.Types.StructureType import StructureType
from SimpleSchema.Schema.Elements.Types.TupleType import TupleType
from SimpleSchema.Schema.Elements.Types.VariantType import VariantType

from SimpleSchema.Schema.Visitors.Visitor import Visitor, VisitResult


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
        return "Diagnostic"

    @property
    @overridemethod
    def description(self) -> str:
        return "Generates a YAML dump of the schema contents."

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(Plugin, self).__init__(
            flags=(
                PluginBase.Flag.AllowRootStructures
                | PluginBase.Flag.AllowNestedStructures
                | PluginBase.Flag.AllowRootItems
                | PluginBase.Flag.AllowNestedItems
                | PluginBase.Flag.AllowRootTypes
                | PluginBase.Flag.AllowNestedTypes
                | PluginBase.Flag.AlwaysDisableUnsupported
            ),
            custom_extension_names=None,
            custom_metadata_attributes=None,
        )

    # ----------------------------------------------------------------------
    @overridemethod
    def GetCommandLineArgs(self) -> TyperEx.TypeDefinitionsType:
        return {}

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
            lambda input_filename, default_output_filename: [default_output_filename.with_suffix(".yaml"), ],
            preserve_dir_structure=preserve_dir_structure,
        )

    # ----------------------------------------------------------------------
    @overridemethod
    def Generate(
        self,
        command_line_args: dict[str, Any],  # pylint: disable=unused-argument
        root: RootStatement,
        output_filenames: list[Path],
        on_status_update_func: Callable[[str], None],
    ) -> None:
        assert len(output_filenames) == 1
        output_filename = output_filenames[0]
        del output_filenames

        on_status_update_func("Generating content...")

        visitor = _Visitor(self)

        root.Accept(
            visitor,
            include_disabled=True,
        )

        on_status_update_func("Writing content...")

        output_filename.parent.mkdir(parents=True, exist_ok=True)

        with output_filename.open("w") as f:
            f.write(ToYamlString(visitor.content))


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _Visitor(Visitor):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        plugin: Plugin,
    ):
        super(_Visitor, self).__init__()

        self._plugin                                    = plugin

        self._content: list[dict[str, Any]]             = []

        self._content_stack: list[list[dict[str, Any]]]                     = [self._content, ]
        self._reference_type_stack: list[ReferenceType]                     = []

    # ----------------------------------------------------------------------
    @property
    def content(self) -> list[dict[str, Any]]:
        assert not self._content_stack
        return self._content

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnElement(self, element: Element) -> Iterator[Optional[VisitResult]]:
        self._content_stack[-1].append(
            {
                "__type__": element.__class__.__name__,
                "__disabled__": element.is_disabled,
                "range": self.__class__._ToString(element.range),    # pylint: disable=protected-access
            },
        )

        if isinstance(element, UniqueNameTrait):
            d = self._content_stack[-1][-1]

            d["unique_name"] = element.unique_name

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnElementChildren(
        self,
        element: Element,
    ) -> Iterator[Optional[VisitResult]]:
        children: list[dict[str, Any]] = []

        self._content_stack.append(children)
        with ExitStack(self._content_stack.pop):
            yield

        self._content_stack[-1][-1][element.CHILDREN_NAME] = children

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnElementDetailsItem(
        self,
        name: str,
        element_or_elements: Element.GenerateAcceptDetailsGeneratorItemsType,
    ) -> Iterator[Optional[VisitResult]]:
        new_items = []

        self._content_stack.append(new_items)
        with ExitStack(self._content_stack.pop):
            yield

        if not isinstance(element_or_elements, list):
            assert len(new_items) == 1
            new_items = new_items[0]

        self._content_stack[-1][-1][name] = new_items

    # ----------------------------------------------------------------------
    # |
    # |  Common
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnCardinality(self, element: Cardinality) -> Iterator[Optional[VisitResult]]:
        value = str(element) or "<single>"

        self._content_stack[-1].pop()
        self._content_stack[-1].append(value)  # type: ignore

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnMetadata(self, element: Metadata) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnMetadataItem(self, element: MetadataItem) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnSimpleElement(self, element: SimpleElement) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        value = element.value

        if isinstance(element.value, (Enum, Path)):
            value = str(value)

        self._content_stack[-1].pop()
        self._content_stack[-1].append(value)  # type: ignore

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    # |
    # |  Expressions
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnBooleanExpression(self, element: BooleanExpression) -> Iterator[Optional[VisitResult]]:
        self._content_stack[-1][-1]["value"] = element.value
        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnIntegerExpression(self, element: IntegerExpression) -> Iterator[Optional[VisitResult]]:
        self._content_stack[-1][-1]["value"] = element.value

        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnListExpression(self, element: ListExpression) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnNoneExpression(self, element: NoneExpression) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnNumberExpression(self, element: NumberExpression) -> Iterator[Optional[VisitResult]]:
        self._content_stack[-1][-1]["value"] = element.value
        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnStringExpression(self, element: StringExpression) -> Iterator[Optional[VisitResult]]:
        self._content_stack[-1][-1]["value"] = element.value
        yield VisitResult.SkipAll

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnTupleExpression(self, element: TupleExpression) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    # |
    # |  Statements
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnExtensionStatement(self, element: ExtensionStatement) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnExtensionStatementKeywordArg(self, element: ExtensionStatementKeywordArg) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnItemStatement(self, element: ItemStatement) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnRootStatement(self, element: RootStatement) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        with ExitStack(self._content_stack.pop):
            yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    # |
    # |  Types
    # |
    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnBooleanType(self, element: BooleanType) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnDateTimeType(self, element: DateTimeType) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnDateType(self, element: DateType) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnDirectoryType(self, element: DirectoryType) -> Iterator[Optional[VisitResult]]:
        self._content_stack[-1][-1]["ensure_exists"] = element.ensure_exists
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnDurationType(self, element: DurationType) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnEnumType(self, element: EnumType) -> Iterator[Optional[VisitResult]]:
        d = self._content_stack[-1][-1]

        d["values"] = [
            {
                "name": e.name,             # type: ignore
                "value": e.value,           # type: ignore
            }
            for e in element.EnumClass      # type: ignore
        ]
        d["starting_value"] = element.starting_value

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnFilenameType(self, element: FilenameType) -> Iterator[Optional[VisitResult]]:
        d = self._content_stack[-1][-1]

        d["ensure_exists"] = element.ensure_exists

        if element.ensure_exists:
            d["match_any"] = element.match_any

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnGuidType(self, element: GuidType) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnIntegerType(self, element: IntegerType) -> Iterator[Optional[VisitResult]]:
        d = self._content_stack[-1][-1]

        if element.min is not None:
            d["min"] = element.min
        if element.max is not None:
            d["max"] = element.max
        if element.bits is not None:
            d["bits"] = str(element.bits)

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnNumberType(self, element: NumberType) -> Iterator[Optional[VisitResult]]:
        d = self._content_stack[-1][-1]

        if element.min is not None:
            d["min"] = element.min
        if element.max is not None:
            d["max"] = element.max
        if element.bits is not None:
            d["bits"] = str(element.bits)

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnReferenceType(self, element: ReferenceType) -> Iterator[Optional[VisitResult]]:
        d = self._content_stack[-1][-1]

        d["display_type"] = element.display_type
        d["flags"] = [
            e.name
            for e in ReferenceType.Flag
            if (element.flags & e.value) and not EnsureValid(e.name).endswith("Mask")
        ]

        if element.is_metadata_resolved:
            resolved_metadata = element.resolved_metadata

            if resolved_metadata:
                metadata: dict[str, dict[str, Any]] = {}

                for k, v in resolved_metadata.items():
                    v.Accept(
                        self,
                        include_disabled=True,
                    )

                    metadata[k] = self._content_stack[-1].pop()

                d["metadata"] = metadata
        else:
            unresolved_metadata = element.unresolved_metadata

            if unresolved_metadata is not None:
                d["metadata"] = unresolved_metadata

        self._reference_type_stack.append(element)
        with ExitStack(self._reference_type_stack.pop):
            yield

        if not (element.flags & ReferenceType.Flag.DefinedInline):
            d["reference"] = {
                "unique_name": element.type.unique_name,
                "range": self.__class__._ToString(element.type.range),  # pylint: disable=protected-access
            }

    # ----------------------------------------------------------------------
    @overridemethod
    def OnReferenceType__type(
        self,
        element_or_elements: Element.GenerateAcceptDetailsGeneratorItemsType,
        *,
        include_disabled: bool,
    ) -> Optional[VisitResult]:
        assert self._reference_type_stack
        reference_type = self._reference_type_stack[-1]

        if not (reference_type.flags & ReferenceType.Flag.DefinedInline):
            # Don't follow this type if it isn't defined inline. We check here rather than
            # preventing visitation in OnReferenceType because we want do display the other
            # details of the reference type (which wouldn't happen if we skipped everything).
            return

        return self._DefaultDetailMethod("type", element_or_elements, include_disabled=include_disabled)

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnStringType(self, element: StringType) -> Iterator[Optional[VisitResult]]:
        d = self._content_stack[-1][-1]

        d["min_length"] = element.min_length

        if element.max_length is not None:
            d["max_length"] = element.max_length
        if element.validation_expression is not None:
            d["validation_expression"] = element.validation_expression

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
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnTupleType(self, element: TupleType) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnUriType(self, element: UriType) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnVariantType(self, element: VariantType) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _ToString(
        value: Any,
    ) -> str:
        if isinstance(value, Range):
            return "{} ({} -> {})".format(value.filename.name, value.begin, value.end)

        assert False, value  # pragma: no cover
