# ----------------------------------------------------------------------
# |
# |  Normalize.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-03-08 13:56:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that normalizes an abstract syntax tree with resolved types"""

import copy

from contextlib import contextmanager
from dataclasses import dataclass
from enum import auto, Enum, IntFlag
from pathlib import Path
from typing import cast, Iterator, Optional, Union

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation.Streams.DoneManager import DoneManager
from Common_Foundation.Types import overridemethod

from Common_FoundationEx import ExecuteTasks

from ...MetadataAttributes.MetadataAttribute import MetadataAttribute

from ...Elements.Common.Element import Element
from ...Elements.Common.Metadata import MetadataItem
from ...Elements.Common.ReferenceCountMixin import ReferenceCountMixin
from ...Elements.Common.SimpleElement import SimpleElement
from ...Elements.Common.Visibility import Visibility

from ...Elements.Expressions.Expression import Expression

from ...Elements.Statements.ExtensionStatement import ExtensionStatement
from ...Elements.Statements.ItemStatement import ItemStatement
from ...Elements.Statements.RootStatement import RootStatement
from ...Elements.Statements.StructureStatement import StructureStatement

from ...Elements.Types.BasicType import BasicType
from ...Elements.Types.ReferenceType import ReferenceType
from ...Elements.Types.StructureType import StructureType

from ...Visitor import Visitor, VisitResult

from ....Common import Errors
from ....Common.ExecuteInParallel import ExecuteInParallel as ExecuteInParallelImpl
from ....Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
class Flag(IntFlag):
    AllowRootItems                          = auto()
    AllowRootStructures                     = auto()
    AllowRootTypes                          = auto()

    AllowNestedItems                        = auto()
    AllowNestedStructures                   = auto()
    AllowNestedTypes                        = auto()

    DisableUnsupportedExtensions            = auto()
    DisableUnsupportedRootElements          = auto()
    DisableUnsupportedNestedElements        = auto()
    DisableUnsupportedMetadata              = auto()

    DisableEmptyStructures                  = auto()
    FlattenStructureHierarchies             = auto()

    # TODO: CollapseTypesWhenPossible               = auto()
    # TODO: RemoveUnusedElements                    = auto()

    # Amalgamations
    AlwaysDisableUnsupported                = (
        DisableUnsupportedExtensions
        | DisableUnsupportedRootElements
        | DisableUnsupportedNestedElements
        | DisableUnsupportedMetadata
    )


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def Normalize(
    dm: DoneManager,
    roots: dict[Path, RootStatement],
    metadata_attributes: list[MetadataAttribute],
    supported_extension_names: set[str],
    flags: Flag,
    *,
    single_threaded: bool=False,
    quiet: bool=False,
    raise_if_single_exception: bool=True,
) -> Optional[dict[Path, Exception]]:
    inherited_attribute_names: set[str] = set(
        metadata_attribute.name
        for metadata_attribute in metadata_attributes
        if metadata_attribute.flags & MetadataAttribute.Flag.Inheritable
    )

    # ----------------------------------------------------------------------
    class Steps(Enum):
        Pass1                               = auto()
        Pass2                               = auto()

    # ----------------------------------------------------------------------
    def Execute(
        root: RootStatement,
        status: ExecuteTasks.Status,
    ) -> None:
        # Pass 1
        status.OnProgress(Steps.Pass1.value, "Pass 1...")

        visitor = _Pass1Visitor(
            inherited_attribute_names,
            supported_extension_names,
            flags,
        )

        root.Accept(visitor)

        # Pass 2
        status.OnProgress(Steps.Pass2.value, "Pass 2...")

        visitor = _Pass2Visitor(
            metadata_attributes,
            flags,
            visitor.all_elements,
            visitor.root_elements,
            visitor.resolved_metadata_cache,
        )

        root.Accept(visitor)

    # ----------------------------------------------------------------------

    results = ExecuteInParallelImpl(
        dm,
        "Normalizing",
        roots,
        Execute,
        quiet=quiet,
        max_num_threads=1 if single_threaded else None,
        raise_if_single_exception=raise_if_single_exception,
        num_steps=len(Steps),
    )

    if dm.result != 0:
        assert all(isinstance(value, Exception) for value in results.values()), results
        return cast(dict[Path, Exception], results)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _ReferenceTypeCategory(Enum):
    Item                                    = auto()
    Structure                               = auto()
    Typedef                                 = auto()
    Base                                    = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _ResolvedMetadataCacheItem(object):
    reference_type: ReferenceType
    unresolved_metadata: dict[str, MetadataItem]


# ----------------------------------------------------------------------
class _Pass1Visitor(Visitor):
    # Pass 1:
    #     - Create unique type names
    #     - Validate:
    #         * Extensions
    #         * ItemStatements
    #         * StructureStatements
    #     - Resolve metadata for all elements that need it
    #     - Flatten any structures that need flattening

    # ----------------------------------------------------------------------
    def __init__(
        self,
        inherited_attribute_names: set[str],
        supported_extension_names: set[str],
        flags: Flag,
    ):
        super(_Pass1Visitor, self).__init__()

        self._inherited_attribute_names     = inherited_attribute_names
        self._supported_extension_names     = supported_extension_names
        self._flags                         = flags

        self._element_stack: list[Element]                                      = []

        self._all_elements: dict[int, Element]                                  = {}
        self._root_elements: set[int]                                           = set()

        self._resolved_metadata_cache: dict[int, _ResolvedMetadataCacheItem]    = {}

    # ----------------------------------------------------------------------
    @property
    def all_elements(self) -> dict[int, Element]:
        assert not self._element_stack
        return self._all_elements

    @property
    def root_elements(self) -> set[int]:
        assert not self._element_stack
        return self._root_elements

    @property
    def resolved_metadata_cache(self) -> dict[int, _ResolvedMetadataCacheItem]:
        assert not self._element_stack
        return self._resolved_metadata_cache

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnElement(self, element: Element) -> Iterator[Optional[VisitResult]]:
        element_id = id(element)

        if element_id in self._all_elements:
            yield VisitResult.SkipAll
            return

        self._all_elements[element_id] = element

        self._element_stack.append(element)
        with ExitStack(self._element_stack.pop):
            if isinstance(element, ReferenceCountMixin):
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

                element.FinalizeUniqueTypeName(".".join(type_name_parts))

            yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnExtensionStatement(self, element: ExtensionStatement) -> Iterator[Optional[VisitResult]]:
        if element.name.value not in self._supported_extension_names:
            if self._flags & Flag.DisableUnsupportedExtensions:
                element.Disable()

                yield VisitResult.SkipAll
                return

            raise Errors.NormalizeInvalidExtension.Create(
                element.name.range,
                element.name.value,
            )

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnItemStatement(self, element: ItemStatement) -> Iterator[Optional[VisitResult]]:
        is_root = len(self._element_stack) == 2  # RootStatement and this Element

        if is_root:
            self._root_elements.add(id(element))

            if not self._flags & Flag.AllowRootItems:
                if self._flags & Flag.DisableUnsupportedRootElements:
                    element.Disable()
                else:
                    raise Errors.NormalizeInvalidRootItem.Create(element.range)

        if not is_root and not self._flags & Flag.AllowNestedItems:
            if self._flags & Flag.DisableUnsupportedNestedElements:
                element.Disable()
            else:
                raise Errors.NormalizeInvalidNestedItem.Create(element.range)

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]:
        # ----------------------------------------------------------------------
        def IsRoot() -> bool:
            # Determine if we are at the root by the number of structure statements that are on the stack
            stack_count = 0

            for stack_element in self._element_stack:
                if isinstance(stack_element, StructureStatement):
                    stack_count += 1

                if stack_count == 2:
                    break

            return stack_count == 1

        # ----------------------------------------------------------------------

        is_root = IsRoot()

        if is_root:
            self._root_elements.add(id(element))

            if not self._flags & Flag.AllowRootStructures:
                if self._flags & Flag.DisableUnsupportedRootElements:
                    element.Disable()
                else:
                    raise Errors.NormalizeInvalidRootStructure.Create(element.range)

        if not is_root and not self._flags & Flag.AllowNestedStructures:
            if self._flags & Flag.DisableUnsupportedNestedElements:
                element.Disable()
            else:
                raise Errors.NormalizeInvalidNestedStructure.Create(element.range)

        yield

        # Flatten
        if self._flags & Flag.FlattenStructureHierarchies:
            items_to_add: list[ItemStatement] = []

            for base_type in element.base_types:
                disable_base_type = True

                with base_type.Resolve() as resolved_base_type:
                    if resolved_base_type.flags & ReferenceType.Flag.StructureRef:
                        assert isinstance(resolved_base_type.type, StructureType), resolved_base_type.type

                        for child in resolved_base_type.type.structure.children:
                            if child.is_disabled or not isinstance(child, ItemStatement):
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
                if not child.is_disabled and isinstance(child, ItemStatement)
            }

            for item_to_add in items_to_add:
                prev_item = item_lookup.get(item_to_add.name.value, None)
                if prev_item is not None:
                    raise Errors.NormalizeDuplicateFlattenedItem.Create(
                        element.range,
                        item_to_add.name.value,
                        item_to_add.name.range,
                        prev_item.range,
                    )

                item_lookup[item_to_add.name.value] = item_to_add

                element.children.append(item_to_add)

        # Disable empty structures
        if self._flags & Flag.DisableEmptyStructures:
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

        if resolved_metadata_key in self._resolved_metadata_cache:
            yield VisitResult.SkipAll
            return

        # Resolve the metadata
        metadata: dict[str, MetadataItem] = (
            {} if element.unresolved_metadata is None else copy.deepcopy(element.unresolved_metadata.items)
        )

        ptr = element.type

        while isinstance(ptr, ReferenceType):
            if ptr.unresolved_metadata is not None:
                for k, v in ptr.unresolved_metadata.items.items():
                    if k in metadata:
                        continue

                    if k not in self._inherited_attribute_names:
                        continue

                    metadata[k] = v

            if ptr.flags & ReferenceType.Flag.Type:
                break

            ptr = ptr.type

        self._resolved_metadata_cache[resolved_metadata_key] = _ResolvedMetadataCacheItem(element, metadata)

        # Apply the element
        is_root = len(self._element_stack) == 2  # RootStatement and this Element

        if is_root:
            self._root_elements.add(id(element))

        # Note that we don't yet have a way to determine the context of this type, so we will
        # validate in a later pass.

        yield


# ----------------------------------------------------------------------
class _Pass2Visitor(Visitor):
    # Pass 2:
    #     - Validate the metadata generated in pass 1
    #     - Calculate the elements that can no longer be referenced

    # ----------------------------------------------------------------------
    def __init__(
        self,
        metadata_attributes: list[MetadataAttribute],
        flags: Flag,
        all_elements: dict[int, Element],
        root_elements: set[int],
        resolved_metadata_cache: dict[int, _ResolvedMetadataCacheItem],
    ):
        super(_Pass2Visitor, self).__init__()

        self._metadata_attributes           = metadata_attributes
        self._flags                         = flags

        self._unvisited_elements            = all_elements
        self._root_elements                 = root_elements
        self._pending_metadata_cache        = resolved_metadata_cache

        self._processed_metadata: set[int]  = set()

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnElement(self, element: Element) -> Iterator[Optional[VisitResult]]:
        if self._unvisited_elements.pop(id(element), None) is None:
            yield VisitResult.SkipAll
            return

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnItemStatement(self, element: ItemStatement) -> Iterator[Optional[VisitResult]]:
        self._ApplyResolvedMetadata(element.type, _ReferenceTypeCategory.Item, element)
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]:
        for base_type in element.base_types:
            if base_type.is_disabled:
                continue

            self._ApplyResolvedMetadata(base_type, _ReferenceTypeCategory.Base, base_type)

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnReferenceType(self, element: ReferenceType) -> Iterator[Optional[VisitResult]]:
        if self._pending_metadata_cache.get(id(element), None) is not None:
            # Create a list of elements that should be disabled atomically if any of the
            # elements in its collection are disabled.
            disabled_elements_set: list[Element] = [element, ]

            if (
                (element.flags & ReferenceType.Flag.StructureRef)
                or (element.flags & ReferenceType.Flag.StructureCollectionRef)
            ):
                reference_type_category = _ReferenceTypeCategory.Structure

                if element.flags & ReferenceType.Flag.StructureRef:
                    assert isinstance(element.type, StructureType), element.type

                    disabled_elements_set += [element.type, element.type.structure, ]
                    referenced_element = element.type.structure

                elif element.flags & ReferenceType.Flag.StructureCollectionRef:
                    assert isinstance(element.type, ReferenceType), element.type
                    assert isinstance(element.type.type, StructureType), element.type.type

                    disabled_elements_set += [
                        element.type,
                        element.type.type,
                        element.type.type.structure,
                    ]

                    referenced_element = element.type.type.structure

                else:
                    assert False, element.flags  # pragma: no cover

            else:
                # We now have enough context to know that this is a typedef. Validate that
                # these are supported.
                is_root = id(element) in self._root_elements

                if is_root and not self._flags & Flag.AllowRootTypes:
                    if self._flags & Flag.DisableUnsupportedRootElements:
                        element.Disable()
                    else:
                        raise Errors.NormalizeInvalidRootType.Create(element.range)

                if not is_root and not self._flags & Flag.AllowNestedTypes:
                    if self._flags & Flag.DisableUnsupportedNestedElements:
                        element.Disable()
                    else:
                        raise Errors.NormalizeInvalidNestedType.Create(element.range)

                reference_type_category = _ReferenceTypeCategory.Typedef
                referenced_element = element

            self._ApplyResolvedMetadata(element, reference_type_category, referenced_element)

            if any(disabled_element.is_disabled for disabled_element in disabled_elements_set):
                for disabled_element in disabled_elements_set:
                    if not disabled_element.is_disabled:
                        disabled_element.Disable()

                yield VisitResult.SkipAll
                return

        yield

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _ApplyResolvedMetadata(
        self,
        reference_type: ReferenceType,
        reference_type_category: _ReferenceTypeCategory,
        referenced_element: Union[
                                            # `reference_type_category` value
            ItemStatement,                  # Item
            StructureStatement,             # Structure
            ReferenceType,                  # Typedef, Base
        ],
    ) -> None:
        cache_key = id(reference_type)

        cache_info = self._pending_metadata_cache.pop(cache_key, None)
        if cache_info is None:
            assert cache_key in self._processed_metadata
            return

        metadata = cache_info.unresolved_metadata
        is_root = id(reference_type) in self._root_elements

        # ----------------------------------------------------------------------
        def GetPotentialError(
            attribute: MetadataAttribute,
        ) -> Optional[str]:
            MetadataFlag = MetadataAttribute.Flag

            # Element type flags
            element_type_flags = attribute.flags & MetadataFlag.ElementTypeMask

            if element_type_flags != 0 and element_type_flags != MetadataFlag.Element:
                if element_type_flags == MetadataFlag.RootElement and not is_root:
                    return Errors.normalize_metadata_element_root

                if element_type_flags == MetadataFlag.NestedElement and is_root:
                    return Errors.normalize_metadata_element_nested

                if element_type_flags & MetadataFlag.Item:
                    if reference_type_category != _ReferenceTypeCategory.Item:
                        return Errors.normalize_metadata_item

                    if element_type_flags == MetadataFlag.RootItem and not is_root:
                        return Errors.normalize_metadata_item_root

                    if element_type_flags == MetadataFlag.NestedItem and is_root:
                        return Errors.normalize_metadata_item_nested

                if element_type_flags & MetadataFlag.Structure:
                    if reference_type_category != _ReferenceTypeCategory.Structure:
                        return Errors.normalize_metadata_structure

                    if element_type_flags == MetadataFlag.RootStructure and not is_root:
                        return Errors.normalize_metadata_structure_root

                    if element_type_flags == MetadataFlag.NestedStructure and is_root:
                        return Errors.normalize_metadata_structure_nested

                if element_type_flags & MetadataFlag.Type:
                    if reference_type_category != _ReferenceTypeCategory.Typedef:
                        return Errors.normalize_metadata_type

                    if element_type_flags == MetadataFlag.RootType and not is_root:
                        return Errors.normalize_metadata_type_root

                    if element_type_flags == MetadataFlag.NestedType and is_root:
                        return Errors.normalize_metadata_type_nested

                if element_type_flags & MetadataFlag.BaseType:
                    if reference_type_category != _ReferenceTypeCategory.Base:
                        return Errors.normalize_metadata_base

            # Cardinality flags
            cardinality_flags = attribute.flags & MetadataFlag.CardinalityMask

            if cardinality_flags != 0:
                with reference_type.Resolve() as resolved_type:
                    cardinality = resolved_type.cardinality

                if cardinality_flags & MetadataFlag.SingleCardinality and not cardinality.is_single:
                    return Errors.normalize_metadata_cardinality_single

                if cardinality_flags & MetadataFlag.OptionalCardinality and not cardinality.is_optional:
                    return Errors.normalize_metadata_cardinality_optional

                if cardinality_flags & MetadataFlag.ContainerCardinality and not cardinality.is_container:
                    return Errors.normalize_metadata_cardinality_container

                if (
                    cardinality_flags & MetadataFlag.ZeroOrMoreCardinality
                    and not (
                        cardinality.is_container
                        and cardinality.min.value == 0
                        and cardinality.max is None
                    )
                ):
                    return Errors.normalize_metadata_cardinality_zero_or_more

                if (
                    cardinality_flags & MetadataFlag.OneOrMoreCardinality
                    and not (
                        cardinality.is_container
                        and cardinality.min.value == 1
                        and cardinality.max is None
                    )
                ):
                    return Errors.normalize_metadata_cardinality_one_or_more

                if (
                    cardinality_flags & MetadataFlag.FixedContainerCardinality
                    and not (
                        cardinality.is_container
                        and cardinality.max is not None
                        and cardinality.max.value == cardinality.min.value
                    )
                ):
                    return Errors.normalize_metadata_cardinality_fixed

            # If here, the metadata is valid in this location
            return None

        # ----------------------------------------------------------------------

        results: dict[str, Union[SimpleElement, Expression]] = {}

        for attribute in self._metadata_attributes:
            attribute_type: ReferenceType = attribute._type  # type: ignore  # pylint: disable=protected-access

            metadata_item = metadata.get(attribute.name, None)

            if metadata_item is None:
                if attribute_type.cardinality.min.value != 0:
                    raise Errors.NormalizeRequiredMetadata.Create(
                        reference_type.unresolved_metadata.range if reference_type.unresolved_metadata is not None else reference_type.range,
                        attribute.name,
                    )

                continue

            potential_error = GetPotentialError(attribute)
            if potential_error is not None:
                raise Errors.NormalizeInvalidMetadata.Create(
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

        if len(results) != len(metadata):
            for metadata_item in metadata.values():
                if not self._flags & Flag.DisableUnsupportedMetadata:
                    raise Errors.NormalizeUnsupportedMetadata.Create(
                        metadata_item.name.range,
                        metadata_item.name.value,
                    )

                results[metadata_item.name.value] = metadata_item.expression
                metadata_item.expression.Disable()

        reference_type.FinalizeMetadata(results)

        self._processed_metadata.add(cache_key)
