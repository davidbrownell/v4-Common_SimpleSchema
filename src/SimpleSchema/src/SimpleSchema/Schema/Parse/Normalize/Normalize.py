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
from dataclasses import dataclass, field
from enum import auto, Enum, IntFlag
from pathlib import Path
from typing import cast, Iterable, Iterator, Optional, Union

from Common_Foundation.Streams.DoneManager import DoneManager
from Common_Foundation.Types import overridemethod

from Common_FoundationEx import ExecuteTasks

from ..Common import PSEUDO_TYPE_NAME_PREFIX

from ...MetadataAttributes.MetadataAttribute import MetadataAttribute

from ...Elements.Common.Cardinality import Cardinality
from ...Elements.Common.Element import Element
from ...Elements.Common.Metadata import MetadataItem
from ...Elements.Common.SimpleElement import SimpleElement
from ...Elements.Common.UniqueNameTrait import UniqueNameTrait
from ...Elements.Common.Visibility import Visibility, VisibilityTrait

from ...Elements.Expressions.Expression import Expression

from ...Elements.Statements.ExtensionStatement import ExtensionStatement
from ...Elements.Statements.ItemStatement import ItemStatement
from ...Elements.Statements.RootStatement import RootStatement
from ...Elements.Statements.StructureStatement import StructureStatement

from ...Elements.Types.BasicType import BasicType
from ...Elements.Types.ReferenceType import ReferenceType
from ...Elements.Types.StructureType import StructureType
from ...Elements.Types.TupleType import TupleType
from ...Elements.Types.VariantType import VariantType

from ...Visitors.DescendantVisitor import DescendantVisitor
from ...Visitors.NonRecursiveVisitor import NonRecursiveVisitor, VisitResult

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

    # For convenience, metadata attribute types are defined with BasicTypes and cardinality
    # values. Convert those values to actual types.
    inherited_attribute_names: set[str] = set()

    for metadata_attribute in metadata_attributes:
        if metadata_attribute.flags & MetadataAttribute.Flag.Inheritable:
            inherited_attribute_names.add(metadata_attribute.name)

        object.__setattr__(
            metadata_attribute,
            _METADATA_ATTRIBUTE_REALIZED_TYPE_ATTRIBUTE_NAME,
            ReferenceType.Create(
                SimpleElement[Visibility](metadata_attribute.type.range, Visibility.Private),
                SimpleElement[str](metadata_attribute.type.range, "Type"),
                metadata_attribute.type,
                metadata_attribute.cardinality,
                None,
            ),
        )


    # ----------------------------------------------------------------------
    class Steps(Enum):
        Step1                               = auto()
        Step2                               = auto()
        Step3                               = auto()

    # ----------------------------------------------------------------------
    def Execute(
        root: RootStatement,
        status: ExecuteTasks.Status,
    ) -> None:
        # Step 1
        status.OnProgress(Steps.Step1.value, "Step 1...")

        visitor = _Step1Visitor(
            inherited_attribute_names,
            supported_extension_names,
            flags,
        )

        root.Accept(visitor)

        root_elements = visitor.root_elements

        # Step 2
        status.OnProgress(Steps.Step2.value, "Step 2...")

        visitor = _Step2Visitor(
            metadata_attributes,
            flags,
            root_elements,
            visitor.inherited_metadata_info_items,
        )

        root.Accept(visitor)

        # Step 3
        status.OnProgress(Steps.Step3.value, "Step 3...")

        root.Accept(_Step3Visitor(flags, root_elements))

    # ----------------------------------------------------------------------

    with dm.VerboseNested("Normalizing types...") as normalizing_dm:
        results = ExecuteInParallelImpl(
            normalizing_dm,
            "Normalizing",
            roots,
            Execute,
            quiet=quiet,
            max_num_threads=1 if single_threaded else None,
            raise_if_single_exception=raise_if_single_exception,
            num_steps=len(Steps),
        )

        if normalizing_dm.result != 0:
            assert all(isinstance(value, Exception) for value in results.values()), results
            return cast(dict[Path, Exception], results)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
_METADATA_ATTRIBUTE_REALIZED_TYPE_ATTRIBUTE_NAME        = "_realized_type"


# ----------------------------------------------------------------------
class _Step1Visitor(NonRecursiveVisitor):
    # Pass 1:
    #     - Create element map
    #     - Create unique type names
    #     - Validate extension statements
    #     - Resolve inherited metadata
    #     - Flatten any structures that can be flattened

    # ----------------------------------------------------------------------
    def __init__(
        self,
        inherited_attribute_names: set[str],
        supported_extension_names: set[str],
        flags: Flag,
    ):
        super(_Step1Visitor, self).__init__()

        self._inherited_attribute_names     = inherited_attribute_names
        self._supported_extension_names     = supported_extension_names
        self._flags                         = flags

        self._root_elements: set[int]                                       = set()
        self._inherited_metadata_info: dict[int, dict[str, MetadataItem]]   = {}

    # ----------------------------------------------------------------------
    @property
    def root_elements(self) -> set[int]:
        return self._root_elements

    @property
    def inherited_metadata_info_items(self) -> dict[int, dict[str, MetadataItem]]:
        assert not self.element_stack
        return self._inherited_metadata_info

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnElement(self, element: Element) -> Iterator[Optional[VisitResult]]:
        # Calculate the root status before we bail if seeing the element for a second time
        # (which is what super's OnElement will do). This ensures that the calculation is valid
        # in scenarios where the element is referenced before it is defined.
        element_key = id(element)

        if (
            element_key not in self._root_elements
            and (
                len(self.element_stack) == 1  # RootStatement
                or (
                    isinstance(element, StructureStatement)
                    and not any(isinstance(stack_item, StructureStatement) for stack_item in self.element_stack)
                )
            )
        ):
            self._root_elements.add(element_key)

        with super(_Step1Visitor, self).OnElement(element) as visit_result:
            if visit_result is not None:
                yield visit_result
                return

            if isinstance(element, UniqueNameTrait):
                type_name_parts: list[str] = [
                    element.name.value
                    for element in self.element_stack
                    if isinstance(element, StructureStatement)
                ]

                if isinstance(element, StructureType):
                    type_name_parts.append(element.display_type)
                elif isinstance(element, BasicType):
                    type_name_parts.append(
                        "{}-Ln{}Col{}".format(
                            element.NAME,
                            element.range.begin.line,
                            element.range.begin.column,
                        ),
                    )
                elif isinstance(element, ReferenceType):
                    type_name_parts.append(element.name.value)
                elif isinstance(element, StructureStatement):
                    # Nothing to do here, as the comprehension statement above will have
                    # captured this name.
                    pass
                else:
                    assert False, element  # pragma: no cover

                element.NormalizeUniqueName(".".join(type_name_parts))

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
    def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]:
        yield

        # Flatten
        if self._flags & Flag.FlattenStructureHierarchies:
            items_to_add: list[ItemStatement] = []

            base_types = element.base_types
            object.__setattr__(element, "base_types", [])

            for base_type in base_types:
                assert not base_type.is_disabled

                with base_type.Resolve() as resolved_base_type:
                    if isinstance(resolved_base_type.type, StructureType):
                        for child in resolved_base_type.type.structure.children:
                            if child.is_disabled or not isinstance(child, ItemStatement):
                                continue

                            items_to_add.append(child)

                    elif isinstance(resolved_base_type.type, BasicType):
                        item_statement = ItemStatement(
                            base_type.range,
                            SimpleElement[Visibility](base_type.range, Visibility.Public),
                            SimpleElement[str](base_type.range, "__value__"),
                            resolved_base_type,
                        )

                        items_to_add.append(item_statement)
                    else:
                        assert False, resolved_base_type  # pragma: no cover

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

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnReferenceType(self, element: ReferenceType) -> Iterator[Optional[VisitResult]]:
        # Create the inherited metadata
        inherited_metadata_key = id(element)
        assert inherited_metadata_key not in self._inherited_metadata_info

        # Resolve the metadata
        metadata_items: dict[str, MetadataItem] = (
            {} if element.unresolved_metadata is None else copy.deepcopy(element.unresolved_metadata.items)
        )

        ptr = element.type

        while isinstance(ptr, ReferenceType):
            if ptr.unresolved_metadata is not None:
                for k, v in ptr.unresolved_metadata.items.items():
                    if k in metadata_items:
                        continue

                    if k not in self._inherited_attribute_names:
                        continue

                    metadata_items[k] = v

            if ptr.category != ReferenceType.Category.Alias:
                break

            ptr = ptr.type

        self._inherited_metadata_info[inherited_metadata_key] = metadata_items

        yield


# ----------------------------------------------------------------------
class _Step2Visitor(NonRecursiveVisitor):
    # Pass 2:
    #     - Validate the metadata generated in pass 1
    #     - Validate element usage based on flags
    #         * ItemStatements
    #         * StructureStatements
    #         * ReferenceTypes
    #     - Collapse Pseudo elements (since they will never be shared)

    # ----------------------------------------------------------------------
    def __init__(
        self,
        metadata_attributes: list[MetadataAttribute],
        flags: Flag,
        root_elements: set[int],
        metadata_items_map: dict[int, dict[str, MetadataItem]],
    ):
        super(_Step2Visitor, self).__init__()

        self._metadata_attributes           = metadata_attributes
        self._flags                         = flags

        self._root_elements                 = root_elements

        self._metadata_items_map            = metadata_items_map

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnItemStatement(self, element: ItemStatement) -> Iterator[Optional[VisitResult]]:
        # Determine if the element placement is valid
        if id(element) in self._root_elements:
            if not self._flags & Flag.AllowRootItems:
                if self._flags & Flag.DisableUnsupportedRootElements:
                    element.Disable()
                else:
                    raise Errors.NormalizeInvalidRootItem.Create(element.range)
        else:
            if not self._flags & Flag.AllowNestedItems:
                if self._flags & Flag.DisableUnsupportedNestedElements:
                    element.Disable()
                else:
                    raise Errors.NormalizeInvalidNestedItem.Create(element.range)

        self._ApplyResolvedMetadata(element.type, MetadataAttribute.Flag.Item, element)
        yield

        # Collapse pseudo elements since they will never be shared
        if (
            isinstance(element.type, ReferenceType)
            and isinstance(element.type.type, ReferenceType)
            and element.type.type.name.value.startswith(PSEUDO_TYPE_NAME_PREFIX)
        ):
            # Disable the pseudo element and convert the alias associated with the item statement
            # into a type that references the generated pseudo element.
            source_type = element.type.type
            dest_type = element.type

            assert source_type.category == ReferenceType.Category.Source, source_type.category
            assert dest_type.category == ReferenceType.Category.Alias, dest_type.category

            object.__setattr__(dest_type, "category", source_type.category)
            object.__setattr__(dest_type, "type", source_type.type)

            source_type.Disable()

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]:
        if id(element) in self._root_elements:
            if not self._flags & Flag.AllowRootStructures:
                if self._flags & Flag.DisableUnsupportedRootElements:
                    element.Disable()
                else:
                    raise Errors.NormalizeInvalidRootStructure.Create(element.range)
        else:
            if not self._flags & Flag.AllowNestedStructures:
                if self._flags & Flag.DisableUnsupportedNestedElements:
                    element.Disable()
                else:
                    raise Errors.NormalizeInvalidNestedStructure.Create(element.range)

        if element.base_types:
            for base_type in element.base_types:
                self._ApplyResolvedMetadata(
                    base_type,
                    MetadataAttribute.Flag.BaseType,
                    base_type,
                    is_root=id(element) in self._root_elements,
                )

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnReferenceType(self, element: ReferenceType) -> Iterator[Optional[VisitResult]]:
        # ----------------------------------------------------------------------
        def IsStructure(
            element: ReferenceType,
        ) -> bool:
            return (
                isinstance(element.type, StructureType)
                and element.cardinality.is_single
                and element.category == ReferenceType.Category.Source
            )

        # ----------------------------------------------------------------------
        def IsStructureContainer(
            element: ReferenceType,
        ) -> bool:
            return (
                isinstance(element.type, ReferenceType)
                and not element.cardinality.is_single
                and element.category == ReferenceType.Category.Source
                and IsStructure(element.type)
            )

        # ----------------------------------------------------------------------

        if self._metadata_items_map.get(id(element), None) is not None:
            if IsStructure(element) or IsStructureContainer(element):
                reference_type_category = MetadataAttribute.Flag.Structure

                if IsStructure(element):
                    assert isinstance(element.type, StructureType), element.type
                    referenced_element = element.type.structure

                elif IsStructureContainer(element):
                    assert isinstance(element.type, ReferenceType), element.type
                    assert isinstance(element.type.type, StructureType), element.type.type

                    referenced_element = element.type.type.structure

                else:
                    assert False, element.type  # pragma: no cover

            else:
                if id(element) in self._root_elements:
                    if not self._flags & Flag.AllowRootTypes:
                        if self._flags & Flag.DisableUnsupportedRootElements:
                            element.Disable()
                        else:
                            raise Errors.NormalizeInvalidRootType.Create(element.range)
                else:
                    if not self._flags & Flag.AllowNestedTypes:
                        if self._flags & Flag.DisableUnsupportedNestedElements:
                            element.Disable()
                        else:
                            raise Errors.NormalizeInvalidNestedType.Create(element.range)

                reference_type_category = MetadataAttribute.Flag.Type
                referenced_element = element

            self._ApplyResolvedMetadata(element, reference_type_category, referenced_element)

        yield

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _ApplyResolvedMetadata(
        self,
        reference_type: ReferenceType,
        reference_type_flags: MetadataAttribute.Flag,
        referenced_element: Union[
                                            # `reference_type_category` value
            ItemStatement,                  # Item
            StructureStatement,             # Structure
            ReferenceType,                  # Typedef, Base
        ],
        *,
        is_root: Optional[bool]=None,
    ) -> None:
        metadata_info_key = id(reference_type)

        metadata_items = self._metadata_items_map.pop(metadata_info_key, None)
        assert metadata_items is not None

        if is_root is None:
            is_root = id(referenced_element) in self._root_elements

        if is_root:
            reference_type_flags |= MetadataAttribute.Flag.Root
        else:
            reference_type_flags |= MetadataAttribute.Flag.Nested

        # ----------------------------------------------------------------------
        def GetPotentialError(
            attribute: MetadataAttribute,
        ) -> Optional[str]:

            # Element type flags
            attribute_flags = attribute.flags & MetadataAttribute.Flag.ElementTypeMask

            if attribute_flags != 0:
                ref_type_flags = reference_type_flags & MetadataAttribute.Flag.ElementTypeMask
                assert ref_type_flags != 0

                if not attribute_flags & ref_type_flags:
                    if attribute_flags & MetadataAttribute.Flag.Item:
                        return Errors.normalize_metadata_item
                    elif attribute_flags & MetadataAttribute.Flag.Structure:
                        return Errors.normalize_metadata_structure
                    elif attribute_flags & MetadataAttribute.Flag.Type:
                        return Errors.normalize_metadata_type
                    elif attribute_flags & MetadataAttribute.Flag.BaseType:
                        return Errors.normalize_metadata_base_type
                    else:
                        assert False, attribute_flags  # pragma: no cover

            # Location type flags
            location_flags = attribute.flags & MetadataAttribute.Flag.LocationTypeMask

            if location_flags != 0:
                ref_type_flags = reference_type_flags & MetadataAttribute.Flag.LocationTypeMask
                assert ref_type_flags != 0

                if not location_flags & reference_type_flags:
                    if attribute_flags & MetadataAttribute.Flag.Item:
                        root_error = Errors.normalize_metadata_item_root
                        nested_error = Errors.normalize_metadata_item_nested
                    elif attribute_flags & MetadataAttribute.Flag.Structure:
                        root_error = Errors.normalize_metadata_structure_root
                        nested_error = Errors.normalize_metadata_structure_nested
                    elif attribute_flags & MetadataAttribute.Flag.Type:
                        root_error = Errors.normalize_metadata_type_root
                        nested_error = Errors.normalize_metadata_type_nested
                    elif attribute_flags & MetadataAttribute.Flag.BaseType:
                        root_error = Errors.normalize_metadata_base_type_root
                        nested_error = Errors.normalize_metadata_base_type_nested
                    else:
                        root_error = Errors.normalize_metadata_element_root
                        nested_error = Errors.normalize_metadata_element_nested

                    if location_flags & MetadataAttribute.Flag.Root:
                        return root_error
                    elif location_flags & MetadataAttribute.Flag.Nested:
                        return nested_error
                    else:
                        assert False, location_flags  # pragma: no cover

            # Cardinality flags
            cardinality_flags = attribute.flags & MetadataAttribute.Flag.CardinalityMask

            if cardinality_flags != 0:
                cardinality = reference_type.cardinality

                errors: list[str] = []
                found_match = False

                if cardinality_flags & MetadataAttribute.Flag.SingleCardinality:
                    if cardinality.is_single:
                        found_match = True
                    else:
                        errors.append(Errors.normalize_metadata_cardinality_single)

                if cardinality_flags & MetadataAttribute.Flag.OptionalCardinality:
                    if cardinality.is_optional:
                        found_match = True
                    else:
                        errors.append(Errors.normalize_metadata_cardinality_optional)

                if cardinality_flags & MetadataAttribute.Flag.ContainerCardinality:
                    if cardinality.is_container:
                        found_match = True
                    else:
                        errors.append(Errors.normalize_metadata_cardinality_container)

                if cardinality_flags & MetadataAttribute.Flag.ZeroOrMoreCardinality:
                    if (
                        cardinality.is_container
                        and cardinality.min.value == 0
                        and cardinality.max is None
                    ):
                        found_match = True
                    else:
                        errors.append(Errors.normalize_metadata_cardinality_zero_or_more)

                if cardinality_flags & MetadataAttribute.Flag.OneOrMoreCardinality:
                    if (
                        cardinality.is_container
                        and cardinality.min.value == 1
                        and cardinality.max is None
                    ):
                        found_match = True
                    else:
                        errors.append(Errors.normalize_metadata_cardinality_one_or_more)

                if cardinality_flags & MetadataAttribute.Flag.FixedContainerCardinality:
                    if (
                        cardinality.is_container
                        and cardinality.max is not None
                        and cardinality.max.value == cardinality.min.value
                    ):
                        found_match = True
                    else:
                        errors.append(Errors.normalize_metadata_cardinality_fixed)

                if not found_match:
                    assert errors, cardinality_flags
                    return errors[0]

            # If here, the metadata is valid in this location
            return None

        # ----------------------------------------------------------------------

        results: dict[str, Union[SimpleElement, Expression]] = {}

        for attribute in self._metadata_attributes:
            realized_type: ReferenceType = cast(ReferenceType, getattr(attribute, _METADATA_ATTRIBUTE_REALIZED_TYPE_ATTRIBUTE_NAME, None))
            assert realized_type is not None

            metadata_item = metadata_items.get(attribute.name, None)

            if metadata_item is None:
                if realized_type.cardinality.min.value != 0:
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

                attribute_value = realized_type.ToPython(metadata_item.expression)

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

        if len(results) != len(metadata_items):
            for metadata_item in metadata_items.values():
                if metadata_item.name.value in results:
                    continue

                if not self._flags & Flag.DisableUnsupportedMetadata:
                    raise Errors.NormalizeUnsupportedMetadata.Create(
                        metadata_item.name.range,
                        metadata_item.name.value,
                    )

                results[metadata_item.name.value] = metadata_item.expression
                metadata_item.expression.Disable()

        reference_type.ResolveMetadata(results)


# ----------------------------------------------------------------------
class _Step3Visitor(NonRecursiveVisitor):
    # Pass3:
    #     - Remove empty structures
    #     - Remove items that are no longer referenced
    #     - Collapse reference types where possible

    # ----------------------------------------------------------------------
    def __init__(
        self,
        flags: Flag,
        root_elements: set[int],
    ):
        super(_Step3Visitor, self).__init__()

        self._flags                         = flags
        self._root_elements                 = root_elements

        self._nodes: dict[int, _Step3Visitor._ElementNode]                  = {}

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnElement(self, element: Element) -> Iterator[Optional[VisitResult]]:
        if isinstance(element, (Cardinality, SimpleElement)):
            yield VisitResult.SkipAll
            return

        # Call the super version after we add information about the reference relationships, as we
        # want to make sure that the information is available before we potentially bail if we have
        # seen the element before.

        element_key = id(element)

        element_node = self._nodes.get(element_key, None)
        if element_node is None:
            element_node = _Step3Visitor._ElementNode(element)
            self._nodes[element_key] = element_node

        if self.element_stack:
            referencing_element_id = id(self.element_stack[-1])

            element_node.referenced_by[referencing_element_id] = self._nodes[referencing_element_id]

        with super(_Step3Visitor, self).OnElement(element) as visit_result:
            if visit_result is not None:
                yield visit_result
                return

            yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnRootStatement(self, element: RootStatement) -> Iterator[Optional[VisitResult]]:
        yield

        self._DisableUnusedRootElements(element)
        self._DisableUnreferencedElements(element)
        self._ResolveReferenceTypeSharedState(element)

        self._CollapseTypes(element)

    # ----------------------------------------------------------------------
    # |  Private Types
    @dataclass(frozen=True)
    class _ElementNode(object):
        # ----------------------------------------------------------------------
        element: Element

        referenced_by: dict[int, "_Step3Visitor._ElementNode"]              = field(init=False, default_factory=dict)

    # ----------------------------------------------------------------------
    # |  Private Methods
    def _DisableUnusedRootElements(
        self,
        root: RootStatement,
    ) -> None:
        for child in root.statements:
            # Disable the child if...
            if (
                not child.is_disabled                                       # ...it isn't already disabled...
                and len(self._nodes[id(child)].referenced_by) == 1          # ...and the root is the only thing that references it...
                and isinstance(child, VisibilityTrait)                      # ...and it has a VisibilityTrait...
                and child.visibility.value != Visibility.Public             # ...and the visibility is not public.
            ):
                child.Disable()

    # ----------------------------------------------------------------------
    def _DisableUnreferencedElements(
        self,
        root: RootStatement,
    ) -> None:
        queue: dict[int, Element] = {}

        # ----------------------------------------------------------------------
        def Enqueue(
            element: Element,
        ) -> None:
            element_key = id(element)

            if element_key not in queue:
                queue[element_key] = element

        # ----------------------------------------------------------------------
        def AreAllDescendantsDisabled(
            element: Element,
        ) -> bool:
            # Prime this value for structures (as a structure is expected to have descendants),
            # but let all others start with the assumption that there aren't descendants
            # until we discover them naturally.
            has_descendant = isinstance(element, StructureStatement)
            has_enabled = False

            # ----------------------------------------------------------------------
            def OnElement(
                query_element: Element,
            ) -> Optional[VisitResult]:
                if query_element is element:
                    return None

                if isinstance(query_element, (Cardinality, SimpleElement)):
                    # These values and their descendants do not impact the
                    # disabled status.
                    return VisitResult.SkipAll

                nonlocal has_descendant
                nonlocal has_enabled

                has_descendant = True

                if not query_element.is_disabled:
                    has_enabled = True

                return VisitResult.SkipAll

            # ----------------------------------------------------------------------

            element.Accept(DescendantVisitor(OnElement), include_disabled=True)

            return has_descendant and not has_enabled

        # ----------------------------------------------------------------------
        def DisableElement(
            element: Element,
        ) -> None:
            descendants: list[Element] = []

            # ----------------------------------------------------------------------
            def OnElement(
                descendant: Element,
            ) -> Optional[VisitResult]:
                if isinstance(descendant, (Cardinality, SimpleElement)):
                    return VisitResult.SkipAll

                if isinstance(descendant, ReferenceType) and descendant.category == ReferenceType.Category.Alias:
                    return VisitResult.SkipAll

                descendants.append(descendant)
                return None

            # ----------------------------------------------------------------------

            element.Accept(DescendantVisitor(OnElement))

            for descendant in descendants:
                assert not descendant.is_disabled
                descendant.Disable()

                nonlocal queue

                for referenced_by in self._nodes[id(descendant)].referenced_by.values():
                    Enqueue(referenced_by.element)

        # ----------------------------------------------------------------------

        for node in self._nodes.values():
            Enqueue(node.element)

        while queue:
            this_element = queue.pop(next(iter(queue.keys())))

            if this_element is root:
                continue

            if this_element.is_disabled:
                continue

            node = self._nodes.get(id(this_element), None)
            assert node is not None

            should_disable = False

            # Disable this element if everything that references it is disabled
            if (
                should_disable is False
                and all(referenced_by.element.is_disabled for referenced_by in node.referenced_by.values())
            ):
                should_disable = True

            # Disable things whose descendants are disabled
            if (
                should_disable is False
                and AreAllDescendantsDisabled(node.element)
                and (
                    not isinstance(node.element, StructureStatement)
                    or self._flags & Flag.DisableEmptyStructures
                )
            ):
                should_disable = True

            if should_disable:
                DisableElement(node.element)

    # ----------------------------------------------------------------------
    def _ResolveReferenceTypeSharedState(
        self,
        root: Element,  # pylint: disable=unused-argument
    ) -> None:
        # ----------------------------------------------------------------------
        def IsShared(
            ref_elements: Iterable[Element],
        ) -> bool:
            count = 0

            for ref_element in ref_elements:
                if ref_element.is_disabled:
                    continue

                if isinstance(ref_element, ReferenceType) and ref_element.category == ReferenceType.Category.Alias:
                    continue

                count += 1
                if count == 2:
                    return True

            return False

        # ----------------------------------------------------------------------

        for node in self._nodes.values():
            if node.element.is_disabled:
                continue

            if not isinstance(node.element, ReferenceType):
                continue

            assert node.referenced_by

            node.element.ResolveIsShared(
                IsShared(ref_node.element for ref_node in node.referenced_by.values()),
            )

    # ----------------------------------------------------------------------
    def _CollapseTypes(
        self,
        root: Element,  # pylint: disable=unused-argument
    ) -> None:
        for node in self._nodes.values():
            if node.element.is_disabled:
                continue

            if not (
                isinstance(node.element, ReferenceType)
                and node.element.category == ReferenceType.Category.Source
                and not node.element.is_shared
                and isinstance(node.element.type, ReferenceType)
            ):
                continue

            assert not node.element.cardinality.is_single
            assert node.element.type.cardinality.is_single

            if id(node.element) in self._root_elements and node.element.visibility.value != Visibility.Private:
                continue

            for ref_by in node.referenced_by.values():
                if ref_by.element.is_disabled:
                    continue

                if isinstance(ref_by.element, ItemStatement):
                    assert not ref_by.element.type.cardinality.is_single

                    node.element.type.Disable()
                    object.__setattr__(ref_by.element.type, "type", node.element.type.type)

                elif isinstance(ref_by.element, ReferenceType):
                    assert ref_by.element.category == ReferenceType.Category.Alias, ref_by.element.category

                    node.element.Disable()

                    object.__setattr__(ref_by.element, "category", node.element.category)
                    object.__setattr__(ref_by.element, "type", node.element.type)

                elif isinstance(ref_by.element, (RootStatement, StructureStatement)):
                    if node.element.visibility.value != Visibility.Private:
                        continue

                    children = getattr(ref_by.element, ref_by.element.CHILDREN_NAME)

                    for statement_index, statement in enumerate(children):
                        if statement is node.element:
                            del children[statement_index]
                            break

                elif isinstance(ref_by.element, (TupleType, VariantType)):
                    types = ref_by.element.types

                    for the_type in types:
                        if the_type is node.element:
                            object.__setattr__(the_type, "type", node.element.type.type)
                            break

                else:
                    assert False, ref_by.element  # pragma: no cover
