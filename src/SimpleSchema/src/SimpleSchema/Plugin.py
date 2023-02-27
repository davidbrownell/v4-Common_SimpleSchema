# ----------------------------------------------------------------------
# |
# |  Plugin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-30 10:08:31
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

import copy

from abc import abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from enum import auto, Enum, IntFlag
from pathlib import Path
from typing import Any, Callable, Iterator, Optional, Protocol, Union

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation.Types import overridemethod

from Common_FoundationEx.CompilerImpl.PluginBase import PluginBase

from .Common import Errors
from .Common.Range import Range
from .Common.SimpleSchemaException import SimpleSchemaException

from .Schema.Elements.Common.Element import Element
from .Schema.Elements.Common.Metadata import MetadataItem
from .Schema.Elements.Common.ReferenceCountMixin import ReferenceCountMixin
from .Schema.Elements.Common.SimpleElement import SimpleElement
from .Schema.Elements.Common.Visibility import Visibility

from .Schema.Elements.Statements.ExtensionStatement import ExtensionStatement
from .Schema.Elements.Statements.ItemStatement import ItemStatement
from .Schema.Elements.Statements.RootStatement import RootStatement
from .Schema.Elements.Statements.StructureStatement import StructureStatement

from .Schema.Elements.Types.BasicType import BasicType
from .Schema.Elements.Types.ReferenceType import ReferenceType
from .Schema.Elements.Types.StructureType import StructureType

from .Schema.MetadataAttributes.ContainerAttributes import PluralNameMetadataAttribute
from .Schema.MetadataAttributes.ElementAttributes import DefaultMetadataAttribute, DescriptionMetadataAttribute, NameMetadataAttribute
from .Schema.MetadataAttributes.MetadataAttribute import MetadataAttribute

from .Schema.Visitor import Visitor, VisitResult


# ----------------------------------------------------------------------
class Plugin(PluginBase):
    """Plugin that generates content based on a SimpleSchema file (or files)"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class Flag(IntFlag):
        AllowRootItems                      = auto()
        AllowRootStructures                 = auto()
        AllowRootTypes                      = auto()

        AllowNestedItems                    = auto()
        AllowNestedStructures               = auto()
        AllowNestedTypes                    = auto()

        AlwaysDisableUnsupportedItems       = auto()

        DisableEmptyStructures              = auto()

        FlattenStructureHierarchies         = auto()

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        flags: Flag,
        custom_extension_names: Optional[set[str]],
        custom_metadata_attributes: Optional[list[MetadataAttribute]],
    ):
        if not (custom_extension_names is None or custom_extension_names):
            raise ValueError("custom_extension_names")
        if not (custom_metadata_attributes is None or custom_metadata_attributes):
            raise ValueError("custom_metadata_attributes")

        metadata_attributes: list[MetadataAttribute] = [
            NameMetadataAttribute(),                    # pylint: disable=no-value-for-parameter
            DescriptionMetadataAttribute(),             # pylint: disable=no-value-for-parameter
            DefaultMetadataAttribute(),                 # pylint: disable=no-value-for-parameter
            PluralNameMetadataAttribute(),              # pylint: disable=no-value-for-parameter
        ]

        metadata_attributes += custom_metadata_attributes or []

        inheritable_attributes: set[str] = set(
            [
                metadata_attribute.name
                for metadata_attribute in metadata_attributes
                if metadata_attribute.flags & MetadataAttribute.Flag.Inheritable
            ],
        )

        # For convenience, metadata attribute types are defined with BasicTypes and cardinality
        # values. Convert those values to actual types.
        for metadata_attribute in metadata_attributes:
            object.__setattr__(
                metadata_attribute,
                "_type",
                ReferenceType.Create(
                    Range.CreateFromCode(),
                    SimpleElement[Visibility](Range.CreateFromCode(), Visibility.Private),
                    SimpleElement[str](Range.CreateFromCode(), "Type"),
                    metadata_attribute.type,
                    metadata_attribute.cardinality,
                    None,
                ),
            )

        self.flags                          = flags

        self._custom_extension_names        = custom_extension_names or set()

        self._custom_metadata_attributes    = metadata_attributes
        self._inheritable_attributes        = inheritable_attributes

    # ----------------------------------------------------------------------
    def Validate(
        self,
        root: RootStatement,
        *,
        filter_unsupported_extensions: bool,
        filter_unsupported_metadata: bool,
        filter_unsupported_root_elements: bool,
        filter_unsupported_nested_elements: bool,
    ) -> None:
        always_filter_override = bool(self.flags & self.Flag.AlwaysDisableUnsupportedItems)

        _Postprocess(
            self,
            root,
            self._inheritable_attributes,
            filter_unsupported_extensions=filter_unsupported_extensions or always_filter_override,
            filter_unsupported_metadata=filter_unsupported_metadata or always_filter_override,
            filter_unsupported_root_elements=filter_unsupported_root_elements or always_filter_override,
            filter_unsupported_nested_elements=filter_unsupported_nested_elements or always_filter_override,
        )

    # ----------------------------------------------------------------------
    @abstractmethod
    def GenerateOutputFilenames(
        self,
        input_root: Path,
        input_filenames: list[Path],
        output_dir: Path,
        *,
        preserve_dir_structure: bool,
    ) -> dict[Path, list[Path]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    def Generate(
        self,
        command_line_args: dict[str, Any],
        root: RootStatement,
        output_filenames: list[Path],
        on_status_update_func: Callable[[str], None],
    ) -> None:
        """Generate output for the provided content"""

        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    def IsValidExtensionName(
        self,
        extension_name: str,
    ) -> bool:
        return extension_name in self._custom_extension_names

    # ----------------------------------------------------------------------
    def GetUniqueTypeName(
        self,
        the_type: ReferenceCountMixin,
    ) -> str:
        result = getattr(
            the_type,
            _UNIQUE_TYPE_NAME_ATTRIBUTE_NAME,
            None,
        )

        assert result is not None
        return result

    # ----------------------------------------------------------------------
    def GetResolvedMetadata(
        self,
        reference_type: ReferenceType,
    ) -> dict[str, SimpleElement]:
        result = getattr(
            reference_type,
            _RESOLVED_METADATA_ATTRIBUTE_NAME,
            None,
        )

        if result is None:
            assert reference_type.is_disabled
            return {}

        return result

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    class _InputFilenameToOutputFilenames_FilenameDecorator(Protocol):
        def __call__(
            self,
            input_filename: Path,
            default_output_filename: Path,
        ) -> list[Path]:
            ...

    @staticmethod
    def _InputFilenameToOutputFilenames(
        input_root: Path,
        input_filenames: list[Path],
        output_dir: Path,
        filename_decorator_func: _InputFilenameToOutputFilenames_FilenameDecorator,
        *,
        preserve_dir_structure: bool,
    ) -> dict[Path, list[Path]]:
        filename_map: dict[Path, list[Path]] = {}

        if preserve_dir_structure:
            len_input_root = len(input_root.parts)

            for input_filename in input_filenames:
                filename_map[input_filename] = filename_decorator_func(
                    input_filename,
                    output_dir / Path(*input_filename.parts[len_input_root:]),
                )

        else:
            filename_lookup: dict[Path, Path] = {}

            for input_filename in input_filenames:
                output_filenames = filename_decorator_func(
                    input_filename,
                    output_dir / input_filename.name,
                )

                for output_filename in output_filenames:
                    existing_input_filename = filename_lookup.get(output_filename, None)

                    if existing_input_filename is not None:
                        raise Exception(
                            Errors.plugin_duplicate_filename.format(
                                output_filename=output_filename,
                                existing_input_filename=existing_input_filename,
                                input_filename=input_filename,
                            ),
                        )

                    filename_lookup[output_filename] = input_filename

                filename_map[input_filename] = output_filenames

        return filename_map


# ----------------------------------------------------------------------
# |
# |  Private Types
# |
# ----------------------------------------------------------------------
_RESOLVED_METADATA_ATTRIBUTE_NAME           = "_resolved_metadata__"
_UNIQUE_TYPE_NAME_ATTRIBUTE_NAME            = "_unique_type_name__"


# ----------------------------------------------------------------------
# |
# |  Private Functions
# |
# ----------------------------------------------------------------------
def _Postprocess(
    plugin: Plugin,
    root: RootStatement,
    inheritable_attribute_names: set[str],
    *,
    filter_unsupported_extensions: bool,
    filter_unsupported_metadata: bool,
    filter_unsupported_root_elements: bool,
    filter_unsupported_nested_elements: bool,
) -> None:
    # Pass 1:
    #     - Create unique type names
    #     - Validate:
    #         * Extensions
    #         * ItemStatements
    #         * StructureStatements
    #     - Resolve metadata for all elements that need it
    #     - Flatten any structures that need flattening

    # ----------------------------------------------------------------------
    class ReferenceTypeCategory(Enum):
        Item                                = auto()
        Structure                           = auto()
        Typedef                             = auto()
        Base                                = auto()

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ResolvedCacheInfo(object):
        reference_type: ReferenceType
        metadata: dict[str, MetadataItem]

    # ----------------------------------------------------------------------

    all_elements: dict[int, Element] = {}
    root_elements: set[int] = set()

    resolved_metadata_cache: dict[int, ResolvedCacheInfo] = {}

    # ----------------------------------------------------------------------
    class Pass1Visitor(Visitor):
        # ----------------------------------------------------------------------
        def __init__(self):
            super(Pass1Visitor, self).__init__()

            self._element_stack: list[Element]          = []

        # ----------------------------------------------------------------------
        @contextmanager
        @overridemethod
        def OnElement(self, element: Element) -> Iterator[Optional[VisitResult]]:
            element_id = id(element)

            if element_id in all_elements:
                yield VisitResult.SkipAll
                return

            all_elements[element_id] = element

            self._element_stack.append(element)
            with ExitStack(self._element_stack.pop):
                if (
                    isinstance(element, ReferenceCountMixin)
                    and getattr(element, _UNIQUE_TYPE_NAME_ATTRIBUTE_NAME, None) is None
                ):
                    type_name_parts: list[str] = [
                        element.name.value
                        for element in self._element_stack
                        if isinstance(element, StructureStatement)
                    ]

                    if isinstance(element, StructureType):
                        type_name_parts.append(element.display_type)
                    elif isinstance(element, BasicType):
                        type_name_parts.append(
                            "{}-Ln{}".format(element.NAME, element.range.begin.line),
                        )
                    elif isinstance(element, ReferenceType):
                        type_name_parts.append(element.name.value)
                    elif isinstance(element, StructureStatement):
                        # Nothing to do here, as the comprehension statement above will have
                        # captured this name.
                        pass
                    else:
                        assert False, element  # pragma: no cover

                    object.__setattr__(
                        element,
                        _UNIQUE_TYPE_NAME_ATTRIBUTE_NAME,
                        ".".join(type_name_parts),
                    )

                yield

        # ----------------------------------------------------------------------
        @contextmanager
        @overridemethod
        def OnExtensionStatement(self, element: ExtensionStatement) -> Iterator[Optional[VisitResult]]:
            if not plugin.IsValidExtensionName(element.name.value):
                if filter_unsupported_extensions:
                    element.Disable()

                    yield VisitResult.SkipAll
                    return

                raise Errors.PluginInvalidExtension.Create(
                    element.name.range,
                    element.name.value,
                    plugin.name,
                )

            yield

        # ----------------------------------------------------------------------
        @contextmanager
        @overridemethod
        def OnItemStatement(self, element: ItemStatement) -> Iterator[Optional[VisitResult]]:
            is_root = len(self._element_stack) == 2  # RootStatement and this Element

            if is_root:
                root_elements.add(id(element))

                if not plugin.flags & Plugin.Flag.AllowRootItems:
                    if filter_unsupported_root_elements:
                        element.Disable()
                    else:
                        raise Errors.PluginInvalidRootItem.Create(element.range, plugin.name)

            if not is_root and not plugin.flags & Plugin.Flag.AllowNestedItems:
                if filter_unsupported_nested_elements:
                    element.Disable()
                else:
                    raise Errors.PluginInvalidNestedItem.Create(element.range, plugin.name)

            yield

        # ----------------------------------------------------------------------
        @contextmanager
        @overridemethod
        def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]:
            # Determine if we are at the root by how many structure statements are on the stack
            stack_structure_statement_count = 0

            for stack_element in self._element_stack:
                if isinstance(stack_element, StructureStatement):
                    stack_structure_statement_count += 1

                if stack_structure_statement_count == 2:
                    break

            is_root = stack_structure_statement_count == 1

            # Validate
            if is_root:
                root_elements.add(id(element))

                if not plugin.flags & Plugin.Flag.AllowRootStructures:
                    if filter_unsupported_root_elements:
                        element.Disable()
                    else:
                        raise Errors.PluginInvalidRootStructure.Create(element.range, plugin.name)

            if not is_root and not plugin.flags & Plugin.Flag.AllowNestedStructures:
                if filter_unsupported_nested_elements:
                    element.Disable()
                else:
                    raise Errors.PluginInvalidNestedStructure.Create(element.range, plugin.name)

            yield

            # Flatten
            if plugin.flags & Plugin.Flag.FlattenStructureHierarchies:
                items_to_add: list[ItemStatement] = []

                for base_type in element.base_types:
                    disable_base_type = True

                    with base_type.Resolve() as resolved_base_type:
                        if resolved_base_type.flags & ReferenceType.Flag.StructureRef:
                            assert isinstance(resolved_base_type.type, StructureType), resolved_base_type.type

                            for child in resolved_base_type.type.structure.children:
                                if not isinstance(child, ItemStatement) or child.is_disabled:
                                    continue

                                items_to_add.append(child)

                        elif resolved_base_type.flags & ReferenceType.Flag.BasicRef:
                            items_to_add.append(
                                ItemStatement(
                                    base_type.range,
                                    SimpleElement[Visibility](base_type.range, Visibility.Public),
                                    SimpleElement[str](base_type.range, "__value__"),
                                    resolved_base_type,
                                ),
                            )

                            disable_base_type = resolved_base_type is not base_type

                        else:
                            assert False, resolved_base_type.flags  # pragma: no cover

                    if disable_base_type:
                        base_type.Disable()

                item_lookup: dict[str, ItemStatement] = {
                    child.name.value: child
                    for child in element.children
                    if isinstance(child, ItemStatement) and not child.is_disabled
                }

                for item_to_add in items_to_add:
                    prev_item = item_lookup.get(item_to_add.name.value, None)
                    if prev_item is not None:
                        raise Errors.PluginDuplicateFlattenedItem.Create(
                            element.range,
                            item_to_add.name.value,
                            item_to_add.name.range,
                            prev_item.range,
                        )

                    element.children.append(item_to_add)

                    item_lookup[item_to_add.name.value] = item_to_add

            # Disable empty structures
            if plugin.flags & Plugin.Flag.DisableEmptyStructures:
                if not any(
                    (
                        not child.is_disabled
                        and (
                            isinstance(child, ItemStatement)
                            or (isinstance(child, ReferenceType) and child.reference_count != 0)
                        )
                    )
                    for child in element.children
                ):
                    element.Disable()

        # ----------------------------------------------------------------------
        @contextmanager
        @overridemethod
        def OnReferenceType(self, element: ReferenceType) -> Iterator[Optional[VisitResult]]:
            resolved_metadata_key = id(element)

            if resolved_metadata_key in resolved_metadata_cache:
                yield VisitResult.SkipAll
                return

            metadata: dict[str, MetadataItem] = (
                {} if element.metadata is None else copy.deepcopy(element.metadata.items)
            )

            ptr = element.type

            while isinstance(ptr, ReferenceType):
                if ptr.metadata is not None:
                    for k, v in ptr.metadata.items.items():
                        if k in metadata:
                            continue

                        if k not in inheritable_attribute_names:
                            continue

                        metadata[k] = v

                if ptr.flags & ReferenceType.Flag.Type:
                    break

                ptr = ptr.type

            is_root = len(self._element_stack) == 2  # RootStatement and this Element

            if is_root:
                root_elements.add(id(element))

            resolved_metadata_cache[resolved_metadata_key] = ResolvedCacheInfo(element, metadata)

            # Note that we don't yet have a way to determine the context of this type, so we will
            # validate in a later pass.

            yield

    # ----------------------------------------------------------------------

    root.Accept(Pass1Visitor())

    # Pass 2:
    #     - Validate the metadata generated in pass 1
    #     - Calculate the elements that can no longer be referenced
    unvisited_elements = all_elements
    del all_elements

    processed_metadata: set[int] = set()

    # ----------------------------------------------------------------------
    class Pass2Visitor(Visitor):
        # ----------------------------------------------------------------------
        @contextmanager
        @overridemethod
        def OnElement(self, element: Element) -> Iterator[Optional[VisitResult]]:
            if unvisited_elements.pop(id(element), None) is None:
                yield VisitResult.SkipAll
                return

            yield

        # ----------------------------------------------------------------------
        @contextmanager
        @overridemethod
        def OnItemStatement(self, element: ItemStatement) -> Iterator[Optional[VisitResult]]:
            self._ApplyResolvedMetadata(element.type, ReferenceTypeCategory.Item, element)
            yield

        # ----------------------------------------------------------------------
        @contextmanager
        @overridemethod
        def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]:
            for base_type in element.base_types:
                if base_type.is_disabled:
                    continue

                self._ApplyResolvedMetadata(base_type, ReferenceTypeCategory.Base, base_type)

            yield

        # ----------------------------------------------------------------------
        @contextmanager
        @overridemethod
        def OnReferenceType(self, element: ReferenceType) -> Iterator[Optional[VisitResult]]:
            if resolved_metadata_cache.get(id(element), None) is not None:
                disabled_query_types: list[Element] = [element]

                if (
                    (element.flags & ReferenceType.Flag.StructureRef)
                    or (element.flags & ReferenceType.Flag.StructureCollectionRef)
                ):
                    referenced_category_type = ReferenceTypeCategory.Structure

                    if element.flags & ReferenceType.Flag.StructureRef:
                        assert isinstance(element.type, StructureType), element.type

                        disabled_query_types += [element.type, element.type.structure, ]
                        referenced_element = element.type.structure

                    elif element.flags & ReferenceType.Flag.StructureCollectionRef:
                        assert isinstance(element.type, ReferenceType), element.type
                        assert isinstance(element.type.type, StructureType), element.type.type

                        disabled_query_types += [
                            element.type,
                            element.type.type,
                            element.type.type.structure,
                        ]

                        referenced_element = element.type.type.structure

                    else:
                        assert False, element.flags  # pragma: no cover

                else:
                    # We now have enough context to know that this is a typedef. Validate that
                    # these are supported by the plugin.
                    is_root = id(element) in root_elements

                    if is_root and not plugin.flags & Plugin.Flag.AllowRootTypes:
                        if filter_unsupported_root_elements:
                            element.Disable()
                        else:
                            raise Errors.PluginInvalidRootType.Create(element.range, plugin.name)

                    if not is_root and not plugin.flags & Plugin.Flag.AllowNestedTypes:
                        if filter_unsupported_nested_elements:
                            element.Disable()
                        else:
                            raise Errors.PluginInvalidNestedType.Create(element.range, plugin.name)

                    referenced_category_type = ReferenceTypeCategory.Typedef
                    referenced_element = element

                self._ApplyResolvedMetadata(element, referenced_category_type, referenced_element)

                if any(query_type.is_disabled for query_type in disabled_query_types):
                    for query_type in disabled_query_types:
                        if not query_type.is_disabled:
                            query_type.Disable()

                    yield VisitResult.SkipAll
                    return

            yield

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        def _ApplyResolvedMetadata(
            self,
            reference_type: ReferenceType,
            referenced_type_category: ReferenceTypeCategory,
            referenced_element: Union[
                                                # `referenced_type_category` value
                ItemStatement,                  # Item
                StructureStatement,             # Structure
                ReferenceType,                  # Typedef, Base
            ],
        ) -> None:
            cache_key = id(reference_type)

            cache_info = resolved_metadata_cache.pop(cache_key, None)
            if cache_info is None:
                assert cache_key in processed_metadata
                return

            metadata = cache_info.metadata
            is_root = id(reference_type) in root_elements

            # Validate
            # ----------------------------------------------------------------------
            def GetPotentialError(
                attribute: MetadataAttribute,
            ) -> Optional[str]:
                Flag = MetadataAttribute.Flag

                # Element type flags
                element_type_flags = attribute.flags & Flag.ElementTypeMask
                if element_type_flags != 0 and element_type_flags != Flag.Element:
                    if element_type_flags == Flag.RootElement and not is_root:
                        return Errors.plugin_metadata_element_root

                    if element_type_flags == Flag.NestedElement and is_root:
                        return Errors.plugin_metadata_element_nested

                    if element_type_flags & Flag.Item:
                        if referenced_type_category != ReferenceTypeCategory.Item:
                            return Errors.plugin_metadata_item

                        if element_type_flags == Flag.RootItem and not is_root:
                            return Errors.plugin_metadata_item_root

                        if element_type_flags == Flag.NestedItem and is_root:
                            return Errors.plugin_metadata_item_nested

                    if element_type_flags & Flag.Structure:
                        if referenced_type_category != ReferenceTypeCategory.Structure:
                            return Errors.plugin_metadata_structure

                        if element_type_flags == Flag.RootStructure and not is_root:
                            return Errors.plugin_metadata_structure_root

                        if element_type_flags == Flag.NestedStructure and is_root:
                            return Errors.plugin_metadata_structure_nested

                    if element_type_flags & Flag.Type:
                        if referenced_type_category != ReferenceTypeCategory.Typedef:
                            return Errors.plugin_metadata_type

                        if element_type_flags == Flag.RootType and not is_root:
                            return Errors.plugin_metadata_type_root

                        if element_type_flags == Flag.NestedType and is_root:
                            return Errors.plugin_metadata_type_nested

                    if element_type_flags & Flag.BaseType:
                        if referenced_type_category != ReferenceTypeCategory.Base:
                            return Errors.plugin_metadata_base

                # Cardinality flags
                cardinality_flags = attribute.flags & Flag.CardinalityMask
                if cardinality_flags != 0:
                    with reference_type.Resolve() as resolved_type:
                        cardinality = resolved_type.cardinality

                    if cardinality_flags & Flag.SingleCardinality and not cardinality.is_single:
                        return Errors.plugin_metadata_cardinality_single

                    if cardinality_flags & Flag.OptionalCardinality and not cardinality.is_optional:
                        return Errors.plugin_metadata_cardinality_optional

                    if cardinality_flags & Flag.ContainerCardinality and not cardinality.is_container:
                        return Errors.plugin_metadata_cardinality_container

                    if (
                        cardinality_flags & Flag.ZeroOrMoreCardinality
                        and not (
                            cardinality.is_container
                            and cardinality.min.value == 0
                            and cardinality.max is None
                        )
                    ):
                        return Errors.plugin_metadata_cardinality_zero_or_more

                    if (
                        cardinality_flags & Flag.OneOrMoreCardinality
                        and not (
                            cardinality.is_container
                            and cardinality.min.value == 1
                            and cardinality.max is None
                        )
                    ):
                        return Errors.plugin_metadata_cardinality_one_or_more

                    if (
                        cardinality_flags & Flag.FixedContainerCardinality
                        and not (
                            cardinality.is_container
                            and cardinality.max is not None
                            and cardinality.min.value == cardinality.max.value
                        )
                    ):
                        return Errors.plugin_metadata_cardinality_fixed

                return None

            # ----------------------------------------------------------------------

            results: dict[str, SimpleElement] = {}

            for attribute in plugin._custom_metadata_attributes:
                attribute_type: ReferenceType = attribute._type # type: ignore  # pylint: disable=protected-access

                metadata_item = metadata.get(attribute.name, None)

                if metadata_item is None:
                    if attribute_type.cardinality.min.value != 0:
                        raise Errors.PluginRequiredMetadata.Create(
                            reference_type.metadata.range if reference_type.metadata is not None else reference_type.range,
                            attribute.name,
                        )

                    continue

                potential_error = GetPotentialError(attribute)
                if potential_error is not None:
                    raise Errors.PluginInvalidMetadata.Create(
                        metadata_item.range,
                        metadata_item.name.value,
                        potential_error,
                    )

                try:
                    attribute.ValidateElement(referenced_element)

                    attribute_value = attribute_type.ToPython(metadata_item.expression)

                    attribute_value = attribute.PostprocessValue(
                        reference_type,
                        attribute_value,
                    )

                    results[attribute.name] = SimpleElement(
                        metadata_item.expression.range,
                        attribute_value,
                    )

                except SimpleSchemaException as ex:
                    ex.ranges.append(metadata_item.range)
                    raise

                except Exception as ex:
                    raise SimpleSchemaException(metadata_item.range, str(ex)) from ex

            if not filter_unsupported_metadata and len(metadata) != len(results):
                for metadata_item in metadata.values():
                    if metadata_item.name.value not in results:
                        raise Errors.PluginUnsupportedMetadata.Create(
                            metadata_item.name.range,
                            metadata_item.name.value,
                            plugin.name,
                        )

            assert getattr(reference_type, _RESOLVED_METADATA_ATTRIBUTE_NAME, None) is None
            object.__setattr__(reference_type, _RESOLVED_METADATA_ATTRIBUTE_NAME, results)

            processed_metadata.add(cache_key)

    # ----------------------------------------------------------------------

    root.Accept(Pass2Visitor())

    # Disable all of the unvisited elements
    for element_id, element in unvisited_elements.items():
        if element_id in root_elements:
            continue

        if not element.is_disabled:
            element.Disable()
