# ----------------------------------------------------------------------
# |
# |  Namespace.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-27 14:16:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
import bisect

from enum import auto, Enum
from pathlib import Path
from typing import Optional, Tuple, Type as PythonType, Union
from weakref import ref, ReferenceType

from .ElementFactories import StructureStatementFactory, TypedefTypeFactory

from ...ANTLR.Elements.Statements.ParseIncludeStatement import ParseIncludeStatement, ParseIncludeStatementType
from ...ANTLR.Elements.Statements.ParseItemStatement import ParseItemStatement
from ...ANTLR.Elements.Statements.ParseStructureStatement import ParseStructureStatement

from ...ANTLR.Elements.Types.ParseIdentifierType import ParseIdentifierType
from ...ANTLR.Elements.Types.ParseTupleType import ParseTupleType
from ...ANTLR.Elements.Types.ParseVariantType import ParseVariantType

from ...ANTLR.Elements.Types.ParseType import ParseType

from ....Elements.Common.Cardinality import Cardinality
from ....Elements.Common.Element import Element
from ....Elements.Common.Metadata import Metadata, MetadataItem
from ....Elements.Common.SimpleElement import SimpleElement
from ....Elements.Common.Visibility import Visibility

from ....Elements.Statements.ItemStatement import ItemStatement
from ....Elements.Statements.RootStatement import RootStatement
from ....Elements.Statements.Statement import Statement
from ....Elements.Statements.StructureStatement import StructureStatement

from ....Elements.Types.FundamentalType import FundamentalType
from ....Elements.Types.StructureType import StructureType
from ....Elements.Types.TupleType import TupleType
from ....Elements.Types.Type import Type
from ....Elements.Types.VariantType import VariantType

from .....Common import Errors
from .....Common.Range import Range


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
class Namespace(object):
    """Manages a collection of types and is associated with a RootStatement, ParseStructureStatement or generated dynamically by a ParseIncludeStatement whose include_type is Named."""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        parent: Optional["Namespace"],
        visibility: Visibility,
        name: str,
        statement: Union[RootStatement, ParseIncludeStatement, ParseStructureStatement],
        structure_statement_factory: Optional[StructureStatementFactory],
    ):
        assert isinstance(statement, (RootStatement, ParseIncludeStatement, ParseStructureStatement)), statement
        assert structure_statement_factory is None or isinstance(statement, ParseStructureStatement), statement

        self._parent_ref: Optional[ReferenceType[Namespace]]                = None if parent is None else ref(parent)

        self.visibility                     = visibility
        self.name                           = name
        self.statement                      = statement
        self.structure_statement_factory    = structure_statement_factory

        self._data                          = _StateControlledData()
        self._included_items: set[int]      = set()

    # ----------------------------------------------------------------------
    @property
    def parent(self) -> Optional["Namespace"]:
        if self._parent_ref is None:
            return None

        parent = self._parent_ref()
        assert parent is not None

        return parent

    @property
    def nested(self) -> dict[str, Union["Namespace", TypedefTypeFactory]]:
        return self._data.final_nested

    # ----------------------------------------------------------------------
    def GetSiblingInfo(
        self,
        element: Element,
    ) -> Tuple[list[Element], int]:
        parent_statement = self.statement

        parents_children = getattr(parent_statement, parent_statement.CHILDREN_NAME)

        for child_index, child in enumerate(parents_children):
            if child is element:
                return parents_children, child_index

        assert False, (parents_children, element)  # pragma: no cover

    # ----------------------------------------------------------------------
    def ParseTypeToType(
        self,
        parse_type: ParseType,
        unique_id: SimpleElement[str],
        ancestors: list[SimpleElement[str]],
        fundamental_types: dict[str, PythonType[FundamentalType]],
    ) -> Type:
        if unique_id in ancestors:
            raise Errors.NamespaceCycle.Create(
                unique_id.range,
                name=unique_id.value,
                ancestors_str="\n".join(
                    "    * '{}' {}".format(ancestor.value, ancestor.range)
                    for ancestor in ancestors
                ),
                ancestors=[(ancestor.value, ancestor.range) for ancestor in ancestors],
            )

        ancestors = ancestors + [unique_id, ]

        if isinstance(parse_type, ParseIdentifierType):
            return self._ParseIdentifierTypeToType(parse_type, ancestors, fundamental_types)

        elif isinstance(parse_type, ParseTupleType):
            return TupleType(
                parse_type.range,
                parse_type.cardinality,
                parse_type.metadata,
                [
                    self.ParseTypeToType(
                        child_type,
                        SimpleElement[str](
                            child_type.range,
                            "{} (Tuple index {})".format(child_type.display_name, child_type_index),
                        ),
                        ancestors,
                        fundamental_types,
                    )
                    for child_type_index, child_type in enumerate(parse_type.types)
                ],
            )

        elif isinstance(parse_type, ParseVariantType):
            return VariantType(
                parse_type.range,
                parse_type.cardinality,
                parse_type.metadata,
                [
                    self.ParseTypeToType(
                        child_type,
                        SimpleElement[str](
                            child_type.range,
                            "{} (Variant index {})".format(child_type.display_name, child_type_index),
                        ),
                        ancestors,
                        fundamental_types,
                    )
                    for child_type_index, child_type in enumerate(parse_type.types)
                ],
            )

        else:
            assert False, parse_type  # pragma: no cover

    # ----------------------------------------------------------------------
    def AddIncludeStatement(
        self,
        statement: ParseIncludeStatement,
    ) -> None:
        self._data.include_statements.append(statement)

    # ----------------------------------------------------------------------
    def AddItemStatement(
        self,
        statement: ParseItemStatement,
    ) -> None:
        assert statement.name.is_expression, statement.name

        if isinstance(self.statement, RootStatement):
            visibility = statement.name.visibility

            if visibility.value == Visibility.Protected:
                raise Errors.NamespaceVisibilityError.Create(visibility.range)

        self._data.item_statements.append(statement)

    # ----------------------------------------------------------------------
    def AddNestedItem(
        self,
        name: SimpleElement[str],
        item: Union["Namespace", TypedefTypeFactory],
    ) -> None:
        if isinstance(self.statement, RootStatement):
            visibility = self.__class__._GetVisibility(item)  # pylint: disable=protected-access

            if visibility.value == Visibility.Protected:
                raise Errors.NamespaceVisibilityError.Create(visibility.range)

        # Insert in sorted order
        bisect.insort(
            self._data.working_nested.setdefault(name.value, []),
            (name.range, item),
            key=lambda v: v[0],
        )

    # ----------------------------------------------------------------------
    def ResolveIncludes(
        self,
        all_namespaces: dict[Path, "Namespace"],
    ) -> None:
        self._data.state = _State.ResolvingIncludes

        # ----------------------------------------------------------------------
        def ApplyIncludedItems(
            parent_namespace: Namespace,
            included_namespace: Namespace,
            include_statement_range: Range,
        ) -> None:
            for key, nested_include_item in included_namespace._data.working_nested.items():  # pylint: disable=protected-access
                # Don't worry if there are multiple values (which indicates an error) right now, as
                # that scenario will be handled later. However, we need this information in order to
                # calculate errors.
                nested_include_item = nested_include_item[0][1]

                if self.__class__._GetVisibility(nested_include_item).value != Visibility.Public:  # pylint: disable=protected-access
                    continue

                parent_namespace.AddNestedItem(
                    SimpleElement[str](include_statement_range, key),
                    nested_include_item,
                )

                parent_namespace._included_items.add(id(nested_include_item))  # pylint: disable=protected-access

        # ----------------------------------------------------------------------

        for statement in self._data.include_statements:
            included_namespace = all_namespaces.get(statement.filename.value, None)
            assert included_namespace is not None, statement.filename

            if statement.include_type == ParseIncludeStatementType.Module:
                module_namespace = Namespace(
                    self.parent,
                    Visibility.Private,
                    statement.filename.value.stem,
                    statement,
                    None,
                )

                ApplyIncludedItems(module_namespace, included_namespace, statement.range)

                self.AddNestedItem(
                    SimpleElement[str](statement.range, module_namespace.name),
                    module_namespace,
                )

            elif statement.include_type == ParseIncludeStatementType.Named:
                for include_item in statement.items:
                    nested_include_item = included_namespace._data.working_nested.get(include_item.element_name.value, None)  # pylint: disable=protected-access
                    if nested_include_item is None:
                        raise Errors.NamespaceInvalidIncludeItem.Create(
                            include_item.element_name.range,
                            include_item.element_name.value,
                        )

                    # Don't worry if there are multiple values (which indicates an error) right now, as
                    # that scenario will be handled later. However, we need this information in order to
                    # calculate errors.
                    nested_include_item = nested_include_item[0][1]

                    if self.__class__._GetVisibility(nested_include_item).value != Visibility.Public:  # pylint: disable=protected-access
                        raise Errors.NamespaceInvalidIncludeItemVisibility.Create(
                            include_item.element_name.range,
                            include_item.element_name.value,
                        )

                    self.AddNestedItem(
                        include_item.reference_name.ToSimpleElement(),
                        nested_include_item,
                    )

                    self._included_items.add(id(nested_include_item))

            elif statement.include_type == ParseIncludeStatementType.Star:
                ApplyIncludedItems(self, included_namespace, statement.range)

            else:
                assert False, statement.include_type  # pragma: no cover

        for nested_values in self._data.working_nested.values():
            nested_value = nested_values[0][1]

            if not isinstance(nested_value, Namespace):
                continue

            if id(nested_value) in self._included_items:
                continue

            nested_value.ResolveIncludes(all_namespaces)

        self._data.state = _State.ResolvedIncludes

    # ----------------------------------------------------------------------
    def ResolveTypeNames(self) -> None:
        self._data.state = _State.ResolvingTypeNames

        nested: dict[str, Union[Namespace, TypedefTypeFactory]] = {}

        for key, nested_values in self._data.working_nested.items():
            nested_value_range, nested_value = nested_values[0]

            self._ValidateTypeName(
                key,
                nested_value_range,
                is_initial_validation=True,
            )

            if (
                isinstance(nested_value, Namespace)
                and id(nested_value) not in self._included_items
            ):
                nested_value.ResolveTypeNames()

            nested[key] = nested_value

        assert not self.nested
        self._data.final_nested.update(nested)

        self._data.state = _State.ResolvedTypeNames

    # ----------------------------------------------------------------------
    def ResolveTypes(
        self,
        fundamental_types: dict[str, PythonType[FundamentalType]],
    ) -> None:
        self._data.state = _State.ResolvingTypes

        # ----------------------------------------------------------------------
        def ReplaceElement(
            existing_statement: Statement,
            new_element: Element,
        ) -> None:
            parents_children, sibling_index = self.GetSiblingInfo(existing_statement)

            parents_children.insert(sibling_index + 1, new_element)

            existing_statement.Disable()

        # ----------------------------------------------------------------------

        for nested_value in self._data.final_nested.values():
            is_import = id(nested_value) in self._included_items

            if isinstance(nested_value, Namespace):
                if not is_import:
                    nested_value.ResolveTypes(fundamental_types)

                if isinstance(nested_value.statement, ParseIncludeStatement):
                    # If here, we are looking at a namespace that was created for a
                    # module import. No need to generate an element based on this
                    # namespace, as there isn't an element that actually exists.
                    assert nested_value.structure_statement_factory is None

                    continue

                assert nested_value.structure_statement_factory is not None
                element_factory = nested_value.structure_statement_factory

            # We can't use isinstance here because importing the type would case a
            # circular reference.
            else:
                element_factory = nested_value

            new_element = element_factory.GetOrCreate([], fundamental_types)

            if not is_import:
                ReplaceElement(element_factory.statement, new_element)

        for item_statement in self._data.item_statements:
            item_statement_name = item_statement.name.ToSimpleElement()

            new_statement = ItemStatement(
                item_statement.range,
                item_statement.name.visibility,
                item_statement_name,
                self.ParseTypeToType(
                    item_statement.type,
                    item_statement_name,
                    [],
                    fundamental_types,
                ),
            )

            ReplaceElement(item_statement, new_statement)

        self._data.state = _State.ResolvedTypes

    # ----------------------------------------------------------------------
    def Finalize(self) -> None:
        self._data.state = _State.Finalizing

        if self.structure_statement_factory:
            self.structure_statement_factory.Finalize()

        for nested_value in self._data.final_nested.values():
            if id(nested_value) not in self._included_items:
                nested_value.Finalize()

        self._data.state = _State.Finalized

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _GetVisibility(
        item: Union["Namespace", TypedefTypeFactory],
    ) -> SimpleElement[Visibility]:
        if isinstance(item, Namespace):
            if isinstance(item.statement, RootStatement):
                # This line will never be invoked, but it just seems wrong not to include it.
                # Disabling coverage on this line.
                return SimpleElement[Visibility](item.statement.range, item.visibility)  # pragma: no cover
            elif isinstance(item.statement, ParseIncludeStatement):
                return SimpleElement[Visibility](item.statement.range, item.visibility)
            elif isinstance(item.statement, ParseStructureStatement):
                return item.statement.name.visibility
            else:
                assert False, item.statement  # pragma: no cover

        # We can't use isinstance here, as that would create a circular dependency
        return item.statement.name.visibility

    # ----------------------------------------------------------------------
    def _ValidateTypeName(
        self,
        name: str,
        range_value: Range,
        *,
        is_initial_validation: bool,
    ) -> None:
        assert self._data.state == _State.ResolvingTypeNames, self._data.state

        error_range: Optional[Range] = None

        values = self._data.working_nested.get(name, None)

        if is_initial_validation:
            assert values is not None

            if len(values) > 1:
                error_range = values[1][0]
        elif values is not None:
            error_range = range_value

        if error_range is not None:
            assert values
            original_range = values[0][0]

            raise Errors.NamespaceDuplicateTypeName.Create(
                error_range,
                name=name,
                original_range=original_range,
            )

        parent = self.parent
        if parent is not None:
            parent._ValidateTypeName(name, range_value, is_initial_validation=False)  # pylint: disable=protected-access

    # ----------------------------------------------------------------------
    def _ParseIdentifierTypeToType(
        self,
        parse_type: ParseIdentifierType,
        ancestors: list[SimpleElement[str]],
        fundamental_types: dict[str, PythonType[FundamentalType]],
    ) -> Type:
        if not parse_type.is_global_reference:
            # ----------------------------------------------------------------------
            def GetNamespacedElement() -> Optional[Element]:
                namespace_root: Optional[Namespace] = self

                while namespace_root is not None:
                    current_namespace = namespace_root

                    for identifier_index, identifier in enumerate(parse_type.identifiers):
                        assert current_namespace is not None

                        potential_namespace_or_factory = current_namespace.nested.get(identifier.value, None)
                        if potential_namespace_or_factory is None:
                            if identifier_index == 0:
                                break

                            raise Errors.NamespaceInvalidType.Create(identifier.range, identifier.value)

                        # TODO: Handle visibility

                        is_last_identifier = identifier_index == len(parse_type.identifiers) - 1

                        if isinstance(potential_namespace_or_factory, Namespace):
                            if is_last_identifier:
                                assert potential_namespace_or_factory.structure_statement_factory is not None
                                return potential_namespace_or_factory.structure_statement_factory.GetOrCreate(ancestors, fundamental_types)

                            current_namespace = potential_namespace_or_factory

                        elif isinstance(potential_namespace_or_factory, TypedefTypeFactory):
                            if is_last_identifier:
                                return potential_namespace_or_factory.GetOrCreate(ancestors, fundamental_types)

                            # The problem isn't with the current identifier, but rather the next one
                            raise Errors.NamespaceInvalidType.Create(
                                parse_type.identifiers[identifier_index + 1].range,
                                parse_type.identifiers[identifier_index + 1].value,
                            )

                        else:
                            assert False, potential_namespace_or_factory  # pragma: no cover

                    namespace_root = namespace_root.parent

                return None

            # ----------------------------------------------------------------------

            namespaced_element = GetNamespacedElement()

            if namespaced_element is not None:
                if isinstance(namespaced_element, Type):
                    the_type = namespaced_element

                    # Resolve the item reference (if necessary)
                    if parse_type.is_item_reference:
                        with the_type.Resolve() as resolved_type:
                            if resolved_type.cardinality.is_single:
                                raise Errors.NamespaceInvalidItemReference.Create(
                                    the_type.range,
                                    the_type.display_name,
                                )

                            the_type = resolved_type.Clone(
                                parse_type.range,
                                Cardinality(parse_type.is_item_reference, None, None),
                            )

                    # Determine if there is type-altering metadata present
                    if parse_type.metadata is not None:
                        with the_type.Resolve() as resolved_type:
                            if resolved_type.cardinality.is_single:
                                type_metadata_items: list[MetadataItem] = []

                                for metadata_item in list(parse_type.metadata.items.values()):
                                    if metadata_item.name.value in resolved_type.FIELDS:
                                        type_metadata_items.append(
                                            parse_type.metadata.items.pop(metadata_item.name.value),
                                        )

                                if type_metadata_items:
                                    the_type = resolved_type.DeriveType(
                                        parse_type.range,
                                        Cardinality(parse_type.range, None, None),
                                        Metadata(parse_type.range, type_metadata_items),
                                    )

                    # Apply cardinality (if necessary)
                    if not parse_type.cardinality.is_single:
                        the_type = the_type.Clone(parse_type.range, parse_type.cardinality)

                    return the_type

                if isinstance(namespaced_element, StructureStatement):
                    if parse_type.is_item_reference:
                        raise Errors.NamespaceStructureItemReference.Create(parse_type.is_item_reference)

                    return StructureType(
                        parse_type.range,
                        parse_type.cardinality,
                        parse_type.metadata,
                        namespaced_element,
                    )

                assert False, namespaced_element  # pragma: no cover

        if len(parse_type.identifiers) == 1:
            fundamental_class = fundamental_types.get(parse_type.identifiers[0].value, None)
            if fundamental_class is not None:
                if parse_type.is_item_reference:
                    raise Errors.NamespaceFundamentalItemReference.Create(parse_type.is_item_reference)

                return fundamental_class.CreateFromMetadata(
                    parse_type.range,
                    parse_type.cardinality,
                    parse_type.metadata,
                )

        raise Errors.NamespaceInvalidType.Create(
            parse_type.identifiers[0].range,
            parse_type.identifiers[0].value,
        )


# ----------------------------------------------------------------------
# |
# |  Private Types
# |
# ----------------------------------------------------------------------
class _State(Enum):
    """Resolving types is a multi-step process; these values represent each step within that process"""

    Initialized                         = auto()

    ResolvingIncludes                   = auto()
    ResolvedIncludes                    = auto()

    ResolvingTypeNames                  = auto()
    ResolvedTypeNames                   = auto()

    ResolvingTypes                      = auto()
    ResolvedTypes                       = auto()

    Finalizing                          = auto()
    Finalized                           = auto()


# ----------------------------------------------------------------------
class _StateControlledData(object):
    """A collection of data whose lifetime is logically controlled by the state"""

    # ----------------------------------------------------------------------
    def __init__(self):
        self._include_statements: list[ParseIncludeStatement]               = []
        self._item_statements: list[ParseItemStatement]                     = []

        self._working_nested: dict[str, list[Tuple[Range, Union[Namespace, TypedefTypeFactory]]]]   = {}
        self._final_nested: dict[str, Union[Namespace, TypedefTypeFactory]]                         = {}

        self._state                         = _State.Initialized

    # ----------------------------------------------------------------------
    @property
    def state(self) -> _State:
        return self._state

    @state.setter
    def state(
        self,
        new_state: _State,
    ) -> None:
        assert new_state.value == self._state.value + 1, (new_state, self._state)
        self._state = new_state

        if self._state == _State.ResolvedIncludes:
            del self._include_statements
        elif self._state == _State.ResolvedTypeNames:
            del self._working_nested
        elif self._state == _State.ResolvedTypes:
            del self._item_statements

    @property
    def include_statements(self) -> list[ParseIncludeStatement]:
        assert self._state.value <= _State.ResolvingIncludes.value
        return self._include_statements

    @property
    def item_statements(self) -> list[ParseItemStatement]:
        assert self._state.value <= _State.ResolvingTypes.value
        return self._item_statements

    @property
    def working_nested(self) -> dict[str, list[Tuple[Range, Union[Namespace, TypedefTypeFactory]]]]:
        assert self._state.value <= _State.ResolvingTypeNames.value
        return self._working_nested

    @property
    def final_nested(self) -> dict[str, Union[Namespace, TypedefTypeFactory]]:
        assert self._state.value >= _State.ResolvingTypeNames.value
        return self._final_nested
