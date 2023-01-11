# ----------------------------------------------------------------------
# |
# |  Namespaces.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-10 15:05:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Namespace and StructureNamespace objects"""

import bisect
import textwrap

from enum import auto, Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Type as TypeOf, Union
from weakref import ref, ReferenceType

from Common_Foundation.Types import extensionmethod, overridemethod

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.Identifier import Identifier, Visibility
from SimpleSchema.Schema.Elements.Common.Range import Range
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Statements.ItemStatement import ItemStatement
from SimpleSchema.Schema.Elements.Statements.StructureStatement import StructureStatement

from SimpleSchema.Schema.Elements.Types.FundamentalType import FundamentalType
from SimpleSchema.Schema.Elements.Types.StructureType import StructureType
from SimpleSchema.Schema.Elements.Types.TupleType import TupleType
from SimpleSchema.Schema.Elements.Types.Type import Type
from SimpleSchema.Schema.Elements.Types.VariantType import VariantType

from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseIncludeStatement import ParseIncludeStatement, ParseIncludeStatementType
from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseItemStatement import ParseItemStatement

from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseIdentifierType import ParseIdentifierType
from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseTupleType import ParseTupleType
from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseType import ParseType
from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseVariantType import ParseVariantType

from SimpleSchema.Schema.Parse.CreateTypeFactory import CreateTypeFactory

from SimpleSchema.Schema.Parse.TypeResolver.ElementFactories import AliasTypeFactory, StructureStatementFactory
from SimpleSchema.Schema.Parse.TypeResolver.TypeConversionKey import TypeConversionKey


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
class Namespace(object):
    """A collection of types within a RootStatement or ParseStructureStatement"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        parent: Optional["Namespace"],
        name: str,
        visibility: Visibility,
    ):
        self._parent_ref: Optional[ReferenceType[Namespace]]                = ref(parent) if parent is not None else None

        self.name                           = name
        self.visibility                     = visibility

        self._data                          = _StateControlledData()

    # ----------------------------------------------------------------------
    @property
    def parent(self) -> Optional["Namespace"]:
        if self._parent_ref is None:
            return None

        parent = self._parent_ref()
        assert parent is not None

        return parent

    @property
    def nested(self) -> Dict[str, Union["StructureNamespace", AliasTypeFactory]]:
        return self._data.final_nested

    # ----------------------------------------------------------------------
    @staticmethod
    def GetVisibility(
        item: Union["StructureNamespace", AliasTypeFactory],
    ) -> Visibility:
        if isinstance(item, StructureNamespace):
            return item.visibility

        # We can't use isinstance as that would create a circular dependency
        return item.statement.name.visibility.value

    # ----------------------------------------------------------------------
    @staticmethod
    def GetSiblingInfo(
        element: Element,
    ) -> Tuple[List[Element], int]:
        assert element.parent is not None

        parents_children = getattr(element.parent, element.parent.CHILDREN_NAME)

        for child_index, child in enumerate(parents_children):
            if child is element:
                return parents_children, child_index

        assert False, (parents_children, element)

    # ----------------------------------------------------------------------
    def ParseTypeToType(
        self,
        parse_type: ParseType,
        key: TypeConversionKey,
        ancestor_keys: List[TypeConversionKey],
        fundamental_types: Dict[str, TypeOf[FundamentalType]],
    ) -> Type:
        if key in ancestor_keys:
            raise SimpleSchemaException(
                textwrap.dedent(
                    """\
                    A cycle was detected in '{}':

                    {}
                    """,
                ).format(
                    key.name,
                    "\n".join(
                        "    - '{}' {}".format(ancestor_key.name, ancestor_key.range.ToString())
                        for ancestor_key in ancestor_keys
                    ),
                ),
                key.range,
            )

        ancestor_keys = ancestor_keys + [key, ]

        if isinstance(parse_type, ParseIdentifierType):
            return self._ParseIdentifierTypeToType(
                parse_type,
                ancestor_keys,
                fundamental_types,
            )

        elif isinstance(parse_type, ParseTupleType):
            return TupleType(
                parse_type.range,
                parse_type.cardinality,
                parse_type.metadata,
                [
                    self.ParseTypeToType(
                        child_type,
                        TypeConversionKey(
                            "{} (Tuple index {})".format(child_type.display_name, child_type_index),
                            child_type.range,
                        ),
                        ancestor_keys,
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
                        TypeConversionKey(
                            "{} (Variant index {})".format(child_type.display_name, child_type_index),
                            child_type.range,
                        ),
                        ancestor_keys,
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
        self._data.item_statements.append(statement)

    # ----------------------------------------------------------------------
    def AddNestedItem(
        self,
        identifier_or_nvp: Union[Identifier, Tuple[str, Range]],
        item: Union["StructureNamespace", AliasTypeFactory],
    ) -> None:
        if isinstance(identifier_or_nvp, Identifier):
            name = identifier_or_nvp.id.value
            range_value = identifier_or_nvp.id.range
        elif isinstance(identifier_or_nvp, tuple):
            name, range_value = identifier_or_nvp
        else:
            assert False, identifier_or_nvp  # pragma: no cover

        # Insert in sorted order
        bisect.insort(
            self._data.working_nested.setdefault(name, []),
            (range_value, item),
            key=lambda v: v[0],
        )

    # ----------------------------------------------------------------------
    def ResolveIncludes(
        self,
        all_namespaces: Dict[Path, "Namespace"],
    ) -> None:
        self._data.state = _State.ResolvingIncludes

        # ----------------------------------------------------------------------
        def ApplyIncludedItems(
            parent_namespace: Namespace,
            included_namespace: Namespace,
            include_statement_range: Range,
        ) -> None:
            for key, nested_include_item in included_namespace._data.working_nested.items():  # pylint: disable=protected-access
                # Don't worry if there are multiple values right now, as that is
                # an error condition that will be addressed when type names are resolved.
                nested_include_item = nested_include_item[0][1]

                if self.__class__.GetVisibility(nested_include_item) != Visibility.Public:
                    continue

                parent_namespace.AddNestedItem((key, include_statement_range), nested_include_item)

        # ----------------------------------------------------------------------

        for statement in self._data.include_statements:
            included_namespace = all_namespaces.get(statement.filename.value, None)
            assert included_namespace is not None

            if statement.include_type == ParseIncludeStatementType.Module:
                ApplyIncludedItems(
                    Namespace(
                        self.parent,
                        statement.filename.value.stem,
                        Visibility.Private,
                    ),
                    included_namespace,
                    statement.range,
                )

            elif statement.include_type == ParseIncludeStatementType.Named:
                for include_item in statement.items:
                    nested_include_item = included_namespace._data.working_nested.get(include_item.element_name.id.value, None)  # pylint: disable=protected-access
                    if nested_include_item is None:
                        raise SimpleSchemaException(
                            "The included item '{}' does not exist.".format(include_item.element_name.id.value),
                            include_item.element_name.id.range,
                        )

                    # Don't worry if there are multiple values right now, as that is
                    # an error condition that will be addressed when type names are resolved.
                    nested_include_item = nested_include_item[0][1]

                    if self.__class__.GetVisibility(nested_include_item) != Visibility.Public:
                        raise SimpleSchemaException(
                            "The included item '{} exists but is not accessible due to its visibility.".format(include_item.element_name.id.value),
                            include_item.element_name.id.range,
                        )

                    self.AddNestedItem(include_item.reference_name, nested_include_item)

            elif statement.include_type == ParseIncludeStatementType.Star:
                ApplyIncludedItems(self, included_namespace, statement.range)

            else:
                assert False, statement.include_type  # pragma: no cover

        for nested_values in self._data.working_nested.values():
            if isinstance(nested_values[0][1], Namespace):
                nested_values[0][1].ResolveIncludes(all_namespaces)

        self._data.state = _State.ResolvedIncludes

    # ----------------------------------------------------------------------
    def ResolveTypeNames(self) -> None:
        self._data.state = _State.ResolvingTypeNames

        nested: Dict[str, Union[StructureNamespace, AliasTypeFactory]] = {}

        for key, values in self._data.working_nested.items():
            self._ValidateTypeName(
                key,
                values[0][0],
                is_initial_validation=True,
            )

            if isinstance(values[0][1], StructureNamespace):
                values[0][1].ResolveTypeNames()

            nested[key] = values[0][1]

        assert not self.nested
        self._data.final_nested.update(nested)

        self._data.state = _State.ResolvedTypeNames

    # ----------------------------------------------------------------------
    def ResolveTypes(
        self,
        fundamental_types: Dict[str, TypeOf[FundamentalType]],
    ) -> None:
        self._data.state = _State.ResolvingTypes

        for nested_value in self._data.final_nested.values():
            if isinstance(nested_value, StructureNamespace):
                nested_value.ResolveTypes(fundamental_types)

                element_factory = nested_value.element_factory
            else:
                # We can't use isinstance as that would create a circular dependency
                element_factory = nested_value

            new_element = element_factory.Create([], fundamental_types)

            # Add the new element and disable the existing one
            original_statement = element_factory.statement

            new_element.SetParent(original_statement.parent)

            parents_children, sibling_index = self.__class__.GetSiblingInfo(original_statement)

            parents_children.insert(sibling_index + 1, new_element)

            original_statement.Disable()

        for item_statement in self._data.item_statements:
            new_item_statement = ItemStatement(
                item_statement.range,
                item_statement.name,
                self.ParseTypeToType(
                    item_statement.type,
                    TypeConversionKey.FromIdentifier(item_statement.name),
                    [],
                    fundamental_types,
                ),
            )

            # Add the new statement and disable the existing one
            new_item_statement.SetParent(item_statement.parent)

            parents_children, sibling_index = self.__class__.GetSiblingInfo(item_statement)

            parents_children.insert(sibling_index + 1, new_item_statement)

            item_statement.Disable()

        self._data.state = _State.ResolvedTypes

    # ----------------------------------------------------------------------
    @extensionmethod
    def Finalize(self) -> None:
        self._data.state = _State.Finalizing

        for nested_value in self._data.final_nested.values():
            nested_value.Finalize()

        self._data.state = _State.Finalized

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    def _ValidateTypeName(
        self,
        name: str,
        range_value: Range,
        *,
        is_initial_validation,
    ) -> None:
        assert self._data.state == _State.ResolvingTypeNames

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

            raise SimpleSchemaException(
                "The type '{}' has already been defined at '{}'.".format(name, original_range.ToString(include_filename=False)),
                error_range,
            )

        if self.parent is not None:
            self.parent._ValidateTypeName(name, range_value, is_initial_validation=False)  # pylint: disable=protected-access

    # ----------------------------------------------------------------------
    def _ParseIdentifierTypeToType(
        self,
        parse_type: ParseIdentifierType,
        ancestor_keys: List[TypeConversionKey],
        fundamental_types: Dict[str, TypeOf[FundamentalType]],
    ) -> Type:
        # ----------------------------------------------------------------------
        def CreateTypeError(
            identifier: Identifier,
        ) -> SimpleSchemaException:
            return SimpleSchemaException(
                "The type '{}'  was not found.".format(identifier.id.value),
                identifier.id.range,
            )

        # ----------------------------------------------------------------------
        def GetNamespacedElement() -> Optional[Element]:
            namespace_root: Optional[Namespace] = self

            while namespace_root is not None:
                current_namespace = namespace_root

                for identifier_index, identifier in enumerate(parse_type.identifiers):
                    assert current_namespace is not None

                    potential_namespace_or_factory = current_namespace.nested.get(identifier.id.value, None)
                    if potential_namespace_or_factory is None:
                        if identifier_index == 0:
                            break

                        raise CreateTypeError(identifier)

                    if self.__class__.GetVisibility(potential_namespace_or_factory) != Visibility.Public:
                        raise SimpleSchemaException(
                            "The type '{}' exists but is not accessible due to its visibility.".format(identifier.id.value),
                            identifier.id.range,
                        )

                    is_last_identifier = identifier_index == len(parse_type.identifiers) - 1

                    if isinstance(potential_namespace_or_factory, StructureNamespace):
                        if is_last_identifier:
                            return potential_namespace_or_factory.element_factory.Create(
                                ancestor_keys,
                                fundamental_types,
                            )

                        current_namespace = potential_namespace_or_factory

                    elif isinstance(potential_namespace_or_factory, AliasTypeFactory):
                        if is_last_identifier:
                            return potential_namespace_or_factory.Create(ancestor_keys, fundamental_types)

                        raise CreateTypeError(parse_type.identifiers[identifier_index + 1])

                    else:
                        assert False, potential_namespace_or_factory  # pragma: no cover

                namespace_root = namespace_root.parent

            return None

        # ----------------------------------------------------------------------

        if not parse_type.is_global_reference:
            namespaced_element = GetNamespacedElement()

            if namespaced_element is not None:
                if isinstance(namespaced_element, Type):
                    namespaced_type = namespaced_element
                elif isinstance(namespaced_element, StructureStatement):
                    namespaced_type = StructureType(
                        parse_type.range,
                        parse_type.cardinality,
                        parse_type.metadata,
                        namespaced_element,
                    )
                else:
                    assert False, namespaced_element  # pragma: no cover

                if parse_type.is_element_reference:
                    return namespaced_type.Clone(
                        range=parse_type.range,
                        cardinality=parse_type.cardinality,
                        metadata=parse_type.metadata,
                    )

                return namespaced_type

        if len(parse_type.identifiers) == 1:
            fundamental_class = fundamental_types.get(parse_type.identifiers[0].id.value, None)
            if fundamental_class is not None:
                if parse_type.is_element_reference:
                    raise SimpleSchemaException(
                        "References to fundamental types cannot specify item references (as they are already item references).",
                        parse_type.is_element_reference,
                    )

                return CreateTypeFactory(fundamental_class)(
                    parse_type.range,
                    parse_type.cardinality,
                    parse_type.metadata,
                )

        raise CreateTypeError(parse_type.identifiers[0])


# ----------------------------------------------------------------------
class StructureNamespace(Namespace):
    """A collection of types made available by a `ParseStructureStatement` instance"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        element_factory: StructureStatementFactory,
        *args,
        **kwargs,
    ):
        super(StructureNamespace, self).__init__(*args, **kwargs)

        self.element_factory                = element_factory

    # ----------------------------------------------------------------------
    @overridemethod
    def Finalize(self) -> None:
        self.element_factory.Finalize()

        super(StructureNamespace, self).Finalize()


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
        self._include_statements: List[ParseIncludeStatement]               = []
        self._item_statements: List[ParseItemStatement]                     = []

        self._working_nested: Dict[str, List[Tuple[Range, Union[StructureNamespace, AliasTypeFactory]]]]    = {}
        self._final_nested: Dict[str, Union[StructureNamespace, AliasTypeFactory]]                          = {}

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
    def include_statements(self) -> List[ParseIncludeStatement]:
        assert self._state.value <= _State.ResolvingIncludes.value
        return self._include_statements

    @property
    def item_statements(self) -> List[ParseItemStatement]:
        assert self._state.value <= _State.ResolvingTypes.value
        return self._item_statements

    @property
    def working_nested(self) -> Dict[str, List[Tuple[Range, Union[StructureNamespace, AliasTypeFactory]]]]:
        assert self._state.value <= _State.ResolvingTypeNames.value
        return self._working_nested

    @property
    def final_nested(self) -> Dict[str, Union[StructureNamespace, AliasTypeFactory]]:
        assert self._state.value >= _State.ResolvingTypeNames.value
        return self._final_nested
