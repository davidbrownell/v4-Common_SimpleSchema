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
from typing import cast, Iterator, Optional, Union

from Common_Foundation.Streams.DoneManager import DoneManager
from Common_Foundation.Types import overridemethod

from Common_FoundationEx import ExecuteTasks

from ..ParseState.ParseState import ParseState

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

    # TODO: CollapseTypesWhenPossible               = auto()

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
    parse_state: ParseState,
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
                metadata_attribute.type.range,
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
            parse_state,
            inherited_attribute_names,
            supported_extension_names,
            flags,
        )

        root.Accept(visitor)

        # Step 2
        status.OnProgress(Steps.Step2.value, "Step 2...")

        visitor = _Step2Visitor(
            metadata_attributes,
            flags,
            visitor.root_elements,
            visitor.inherited_metadata_info_items,
        )

        root.Accept(visitor)

        # Step 3
        status.OnProgress(Steps.Step3.value, "Step 3...")

        root.Accept(_Step3Visitor(flags))

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
    #     - Validate element usage based on flags
    #         * Extensions
    #         * ItemStatements
    #         * StructureStatements
    #     - Resolve inherited metadata
    #     - Flatten any structures that can be flattened

    # ----------------------------------------------------------------------
    def __init__(
        self,
        parse_state: ParseState,
        inherited_attribute_names: set[str],
        supported_extension_names: set[str],
        flags: Flag,
    ):
        super(_Step1Visitor, self).__init__()

        self._parse_state                   = parse_state
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

        is_root = len(self.element_stack) == 2  # RootStatement and this Element

        if is_root:
            self._root_elements.add(id(element))

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnItemStatement(self, element: ItemStatement) -> Iterator[Optional[VisitResult]]:
        is_root = len(self.element_stack) == 2  # RootStatement and this Element

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

            for stack_element in self.element_stack:
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

            base_types = element.base_types
            object.__setattr__(element, "base_types", [])

            for base_type in base_types:
                assert not base_type.is_disabled

                with base_type.Resolve() as resolved_base_type:
                    if resolved_base_type.flags & ReferenceType.Flag.StructureRef:
                        assert isinstance(resolved_base_type.type, StructureType), resolved_base_type.type

                        for child in resolved_base_type.type.structure.children:
                            if child.is_disabled or not isinstance(child, ItemStatement):
                                continue

                            items_to_add.append(child)

                    elif resolved_base_type.flags & ReferenceType.Flag.BasicRef:
                        item_statement = ItemStatement(
                            base_type.range,
                            SimpleElement[Visibility](base_type.range, Visibility.Public),
                            SimpleElement[str](base_type.range, "__value__"),
                            resolved_base_type,  # type: ignore
                        )

                        items_to_add.append(item_statement)

                    else:
                        assert False, resolved_base_type.flags  # pragma: no cover

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
        is_root = len(self.element_stack) == 2  # RootStatement and this Element

        if is_root:
            self._root_elements.add(id(element))

        # Note that we don't yet have a way to determine the context of this type, so we will
        # validate in a later pass.

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

            if ptr.flags & ReferenceType.Flag.Type:
                break

            ptr = ptr.type

        self._inherited_metadata_info[inherited_metadata_key] = metadata_items

        yield


# ----------------------------------------------------------------------
class _Step2Visitor(NonRecursiveVisitor):
    # Pass 2:
    #     - Validate the metadata generated in pass 1
    #     - Reduce elements

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
        self._ApplyResolvedMetadata(element.type, MetadataAttribute.Flag.Item, element)
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]:
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
        if self._metadata_items_map.get(id(element), None) is not None:
            if (
                (element.flags & ReferenceType.Flag.StructureRef)
                or (element.flags & ReferenceType.Flag.StructureCollectionRef)
            ):
                reference_type_category = MetadataAttribute.Flag.Structure

                if element.flags & ReferenceType.Flag.StructureRef:
                    assert isinstance(element.type, StructureType), element.type
                    referenced_element = element.type.structure

                elif element.flags & ReferenceType.Flag.StructureCollectionRef:
                    assert isinstance(element.type, ReferenceType), element.type
                    assert isinstance(element.type.type, StructureType), element.type.type

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

    # ----------------------------------------------------------------------
    def __init__(
        self,
        flags: Flag,
    ):
        super(_Step3Visitor, self).__init__()

        self._flags                         = flags

        self._nodes: dict[int, _Step3Visitor._ElementNode]                  = {}

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnElement(self, element: Element) -> Iterator[Optional[VisitResult]]:
        referencing_element = None if not self.element_stack else self.element_stack[-1]

        with super(_Step3Visitor, self).OnElement(element) as visit_result:
            if visit_result is not None:
                yield visit_result
                return

            element_key = id(element)

            element_node = self._nodes.get(element_key, None)
            if element_node is None:
                element_node = _Step3Visitor._ElementNode(element)
                self._nodes[element_key] = element_node

            # Maintain the references if....
            if (
                referencing_element                                         # ...this element is not the root element
                and (                                                       # ...and...
                    not isinstance(referencing_element, RootStatement)      # ...it is not at the root...
                    or not isinstance(element, VisibilityTrait)             # ...or isn't based on VisibilityTrait...
                    or element.visibility.value == Visibility.Public        # ...or has a visibility and the visibility is public
                )
            ):
                element_node.referenced_by[id(referencing_element)] = referencing_element

            yield

    # ----------------------------------------------------------------------
    @contextmanager
    @overridemethod
    def OnRootStatement(self, element: RootStatement) -> Iterator[Optional[VisitResult]]:
        yield

        queue: list[Element] = [node.element for node in self._nodes.values()]

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
                descendants.append(descendant)
                return None

            # ----------------------------------------------------------------------

            element.Accept(DescendantVisitor(OnElement))

            for descendant in descendants:
                assert not descendant.is_disabled
                descendant.Disable()

                nonlocal queue
                queue += self._nodes[id(descendant)].referenced_by.values()

        # ----------------------------------------------------------------------

        while queue:
            this_element = queue.pop(0)

            if this_element is element:
                continue

            if this_element.is_disabled:
                continue

            node = self._nodes.get(id(this_element), None)
            assert node is not None

            should_disable = False

            # Disable this element if everything that references it is disabled
            if (
                should_disable is False
                and all(referenced_by.is_disabled for referenced_by in node.referenced_by.values())
            ):
                should_disable = True

            # Disable things whose descendants are disabled?
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
    # |  Private Types
    @dataclass(frozen=True)
    class _ElementNode(object):
        element: Element

        referenced_by: dict[int, Element]   = field(init=False, default_factory=dict)
