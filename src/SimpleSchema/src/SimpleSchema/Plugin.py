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
from dataclasses import dataclass, field
from enum import auto, Enum, IntFlag
from pathlib import Path
from typing import Any, Callable, Iterator, Optional, Protocol, Union

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation.Types import overridemethod

from Common_FoundationEx.CompilerImpl.PluginBase import PluginBase

from .Common import Errors

from .Schema.Elements.Common.Element import Element
from .Schema.Elements.Common.Metadata import MetadataItem
from .Schema.Elements.Common.SimpleElement import SimpleElement

from .Schema.Elements.Statements.ExtensionStatement import ExtensionStatement
from .Schema.Elements.Statements.ItemStatement import ItemStatement
from .Schema.Elements.Statements.RootStatement import RootStatement
from .Schema.Elements.Statements.StructureStatement import StructureStatement

from .Schema.Elements.Types.BasicType import BasicType
from .Schema.Elements.Types.ReferenceType import ReferenceType
from .Schema.Elements.Types.StructureType import StructureType

from .Schema.MetadataAttributes.ContainerAttributes import PluralNameMetadataAttribute
from .Schema.MetadataAttributes.ElementAttributes import DescriptionMetadataAttribute, NameMetadataAttribute
from .Schema.MetadataAttributes.MetadataAttribute import MetadataAttribute
from .Schema.MetadataAttributes.OptionalAttributes import DefaultMetadataAttribute

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

        AllowNestedItems                    = auto()
        AllowNestedStructures               = auto()

        CreateDottedNames                   = auto()

        SkipEmptyStructures                 = auto()
        AlwaysFilterUnsupportedItems        = auto()

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
        always_filter_override = bool(self.flags & self.Flag.AlwaysFilterUnsupportedItems)

        _Validate(
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
    def InitDottedName(
        self,
        reference_type_category: "_ReferenceTypeCategory",  # pylint: disable=unused-argument
        elements: list[Element],
        *,
        is_root: bool,  # pylint: disable=unused-argument
    ) -> None:
        if not self.flags & Plugin.Flag.CreateDottedNames:
            return

        assert elements
        assert isinstance(elements[-1], (BasicType, ReferenceType))

        # Do we have a cached value?
        if getattr(
            elements[-1],
            self.__class__._DOTTED_NAME_ATTRIBUTE_NAME,  # pylint: disable=protected-access
            None,
        ) is not None:
            return

        # Calculate the result
        dotted_name_parts: list[str] = [
            element.name.value
            for element in elements
            if isinstance(element, StructureStatement)
        ]

        if isinstance(elements[-1], BasicType):
            dotted_name_parts.append(elements[-1].NAME)
        elif isinstance(elements[-1], ReferenceType):
            dotted_name_parts.append(elements[-1].name.value)
        else:
            assert False, elements[-1]  # pragma: no cover

        dotted_name = ".".join(dotted_name_parts)

        # Cache the result
        object.__setattr__(
            elements[-1],
            self.__class__._DOTTED_NAME_ATTRIBUTE_NAME,  # pylint: disable=protected-access
            dotted_name,
        )

    # ----------------------------------------------------------------------
    def InitResolvedMetadata(
        self,
        reference_type_category: "_ReferenceTypeCategory",
        reference_element: Element,
        reference_type: ReferenceType,
        metadata: dict[str, MetadataItem],
        *,
        is_root: bool,
        filter_unsupported_metadata: bool,
    ) -> None:
        assert getattr(
            reference_type,
            self.__class__._RESOLVED_METADATA_ATTRIBUTE_NAME,  # pylint: disable=protected-access
            None,
        ) is None

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
                    if reference_type_category != _ReferenceTypeCategory.Item:
                        return Errors.plugin_metadata_item

                    if element_type_flags == Flag.RootItem and not is_root:
                        return Errors.plugin_metadata_item_root

                    if element_type_flags == Flag.NestedItem and is_root:
                        return Errors.plugin_metadata_item_nested

                if element_type_flags & Flag.Structure:
                    if reference_type_category != _ReferenceTypeCategory.Structure:
                        return Errors.plugin_metadata_structure

                    if element_type_flags == Flag.RootStructure and not is_root:
                        return Errors.plugin_metadata_structure_root

                    if element_type_flags == Flag.NestedStructure and is_root:
                        return Errors.plugin_metadata_structure_nested

                if element_type_flags & Flag.Type:
                    if reference_type_category != _ReferenceTypeCategory.Typedef:
                        return Errors.plugin_metadata_type

                    if element_type_flags == Flag.RootType and not is_root:
                        return Errors.plugin_metadata_type_root

                    if element_type_flags == Flag.NestedType and is_root:
                        return Errors.plugin_metadata_type_nested

                if element_type_flags & Flag.BaseType:
                    if reference_type_category != _ReferenceTypeCategory.Base:
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

        for attribute in self._custom_metadata_attributes:
            metadata_item = metadata.get(attribute.name, None)

            if metadata_item is None:
                if attribute.type.cardinality.min.value != 0:
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

            attribute.Validate(reference_element)

            attribute_value = attribute.type.ToPython(metadata_item.expression)

            results[attribute.name] = SimpleElement(
                metadata_item.expression.range,
                attribute_value,
            )

        if not filter_unsupported_metadata and len(metadata) != len(results):
            for metadata_item in metadata.values():
                if metadata_item.name.value not in results:
                    raise Errors.PluginUnsupportedMetadata.Create(
                        metadata_item.name.range,
                        metadata_item.name.value,
                        self.name,
                    )

        # Commit the results
        object.__setattr__(
            reference_type,
            self.__class__._RESOLVED_METADATA_ATTRIBUTE_NAME,  # pylint: disable=protected-access
            results,
        )

    # ----------------------------------------------------------------------
    def GetResolvedMetadata(
        self,
        reference_type: ReferenceType,
    ) -> dict[str, SimpleElement]:
        result = getattr(
            reference_type,
            self.__class__._RESOLVED_METADATA_ATTRIBUTE_NAME,  # pylint: disable=protected-access
            None,
        )

        assert result is not None
        return result

    # ----------------------------------------------------------------------
    def GetDottedName(
        self,
        the_type: Union[BasicType, ReferenceType],
    ) -> str:
        result = getattr(
            the_type,
            self.__class__._DOTTED_NAME_ATTRIBUTE_NAME,  # pylint: disable=protected-access
            None,
        )

        assert result is not None
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
    _RESOLVED_METADATA_ATTRIBUTE_NAME       = "_resolved_metadata__"
    _DOTTED_NAME_ATTRIBUTE_NAME             = "_dotted_name__"


# ----------------------------------------------------------------------
# |
# |  Private Types
# |
# ----------------------------------------------------------------------
class _ReferenceTypeCategory(Enum):
    Unknown                                 = 0
    Item                                    = auto()
    Structure                               = auto()
    Typedef                                 = auto()
    Base                                    = auto()


# ----------------------------------------------------------------------
def _Validate(
    plugin: Plugin,
    root: RootStatement,
    inheritable_attribute_names: set[str],
    *,
    filter_unsupported_extensions: bool,
    filter_unsupported_metadata: bool,
    filter_unsupported_root_elements: bool,
    filter_unsupported_nested_elements: bool,
) -> None:
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class CacheInfo(object):
        metadata: dict[str, MetadataItem]
        is_root: bool                       = field(kw_only=True)

    # ----------------------------------------------------------------------

    metadata_cache: dict[int, CacheInfo] = {}
    processed_metadata: set[int] = set()

    # Note that this algorithm must be done in 2 passes (I think) because ReferenceType is greedy
    # (given that it is visiting the elements using depth-first traversal) when attempting to
    # assign metadata when it is called. Unfortunately, we don't always have the context necessary
    # to assign metadata when this happens on the first pass (as is the case with StructureTypes
    # and ReferenceTypes that are Typedefs). So, generate the metadata on pass 1 and assign the
    # metadata on pass 2.

    # ----------------------------------------------------------------------
    class Pass1Visitor(Visitor):
        # ----------------------------------------------------------------------
        def __init__(self):
            super(Pass1Visitor, self).__init__()

            self._element_stack: list[Element]          = []

            if plugin.flags & Plugin.Flag.CreateDottedNames:
                # ----------------------------------------------------------------------
                def CreateDottedNames() -> None:
                    assert self._element_stack

                    if isinstance(self._element_stack[-1], (BasicType, ReferenceType)):
                        plugin.InitDottedName(
                            _ReferenceTypeCategory.Unknown,
                            self._element_stack,
                            is_root=len(self._element_stack) == 2,  # RootStatement then this Element
                        )

                # ----------------------------------------------------------------------

                created_dotted_names_func = CreateDottedNames
            else:
                created_dotted_names_func = lambda: None

            self._created_dotted_names_func             = created_dotted_names_func

        # ----------------------------------------------------------------------
        @contextmanager
        @overridemethod
        def OnElement(self, element: Element) -> Iterator[Optional[VisitResult]]:
            self._element_stack.append(element)
            with ExitStack(self._element_stack.pop):
                self._created_dotted_names_func()

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

            if is_root and not plugin.flags & Plugin.Flag.AllowRootItems:
                if filter_unsupported_root_elements:
                    element.Disable()

                    yield VisitResult.SkipAll
                    return

                raise Errors.PluginInvalidRootItem.Create(element.range, plugin.name)

            if not is_root and not plugin.flags & Plugin.Flag.AllowNestedItems:
                if filter_unsupported_nested_elements:
                    element.Disable()

                    yield VisitResult.SkipAll
                    return

                raise Errors.PluginInvalidNestedItem.Create(element.range, plugin.name)

            yield

        # ----------------------------------------------------------------------
        @contextmanager
        @overridemethod
        def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]:
            if not element.children and plugin.flags & Plugin.Flag.SkipEmptyStructures:
                element.Disable()

                yield VisitResult.SkipAll
                return

            stack_structure_statement_count = 0

            for stack_element in self._element_stack:
                if isinstance(stack_element, StructureStatement):
                    stack_structure_statement_count += 1

                if stack_structure_statement_count == 2:
                    break

            is_root = stack_structure_statement_count == 1

            if is_root and not plugin.flags & Plugin.Flag.AllowRootStructures:
                if filter_unsupported_root_elements:
                    element.Disable()

                    yield VisitResult.SkipAll
                    return

                raise Errors.PluginInvalidRootStructure.Create(element.range, plugin.name)

            if not is_root and not plugin.flags & Plugin.Flag.AllowNestedStructures:
                if filter_unsupported_nested_elements:
                    element.Disable()

                    yield VisitResult.SkipAll
                    return

                raise Errors.PluginInvalidNestedStructure.Create(element.range, plugin.name)

            yield

        # ----------------------------------------------------------------------
        @contextmanager
        @overridemethod
        def OnReferenceType(self, element: ReferenceType) -> Iterator[Optional[VisitResult]]:
            cache_key = id(element)

            if cache_key in metadata_cache:
                yield VisitResult.SkipAll
                return

            metadata: dict[str, MetadataItem] = (
                {} if element.metadata is None else copy.deepcopy(element.metadata.items)
            )

            while (
                (element.flags & ReferenceType.Flag.Alias)
                and not (element.flags & ReferenceType.Flag.BasicRef)
            ):
                assert isinstance(element.type, ReferenceType), element.type
                element = element.type

                if element.metadata is None:
                    continue

                for k, v in element.metadata.items.items():
                    if k in metadata:
                        continue

                    if k not in inheritable_attribute_names:
                        continue

                    metadata[k] = v

            metadata_cache[cache_key] = CacheInfo(
                metadata,
                is_root=len(self._element_stack) == 2,  # RootStatement and this Element
            )

            yield

    # ----------------------------------------------------------------------
    class Pass2Visitor(Visitor):
        # ----------------------------------------------------------------------
        @contextmanager
        @overridemethod
        def OnItemStatement(self, element: ItemStatement) -> Iterator[Optional[VisitResult]]:
            cache_key = id(element.type)

            cache_info = metadata_cache.pop(cache_key, None)
            if cache_info is None:
                assert cache_key in processed_metadata

                yield VisitResult.SkipAll
                return

            plugin.InitResolvedMetadata(
                _ReferenceTypeCategory.Item,
                element,
                element.type,
                cache_info.metadata,
                is_root=cache_info.is_root,
                filter_unsupported_metadata=filter_unsupported_metadata,
            )

            processed_metadata.add(cache_key)

            yield

        # ----------------------------------------------------------------------
        @contextmanager
        @overridemethod
        def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]:
            for base_type in element.base_types:
                cache_key = id(base_type)

                cache_info = metadata_cache.pop(cache_key, None)
                if cache_info is None:
                    assert cache_key in processed_metadata
                    continue

                plugin.InitResolvedMetadata(
                    _ReferenceTypeCategory.Base,
                    base_type,
                    base_type,
                    cache_info.metadata,
                    is_root=cache_info.is_root,
                    filter_unsupported_metadata=filter_unsupported_metadata,
                )

                processed_metadata.add(cache_key)

            yield

        # ----------------------------------------------------------------------
        @contextmanager
        @overridemethod
        def OnReferenceType(self, element: ReferenceType) -> Iterator[Optional[VisitResult]]:
            cache_key = id(element)

            cache_info = metadata_cache.pop(cache_key, None)

            if cache_info is None:
                assert cache_key in processed_metadata
            else:
                if element.flags & ReferenceType.Flag.StructureRef:
                    category_type = _ReferenceTypeCategory.Structure

                    assert isinstance(element.type, StructureType), element.type
                    reference_element = element.type.structure

                elif element.flags & ReferenceType.Flag.StructureCollectionRef:
                    category_type = _ReferenceTypeCategory.Structure

                    assert isinstance(element.type, ReferenceType), element.type
                    assert isinstance(element.type.type, StructureType), element.type.type

                    reference_element = element.type.type.structure

                else:
                    category_type = _ReferenceTypeCategory.Typedef
                    reference_element = element

                plugin.InitResolvedMetadata(
                    category_type,
                    reference_element,
                    element,
                    cache_info.metadata,
                    is_root=cache_info.is_root,
                    filter_unsupported_metadata=filter_unsupported_metadata,
                )

                processed_metadata.add(cache_key)

            yield

    # ----------------------------------------------------------------------

    root.Accept(Pass1Visitor())

    if metadata_cache:
        root.Accept(Pass2Visitor())
