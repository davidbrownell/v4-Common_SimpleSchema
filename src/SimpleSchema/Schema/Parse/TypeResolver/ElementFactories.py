# ----------------------------------------------------------------------
# |
# |  ElementFactories.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-10 14:14:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the AliasTypeFactory and StructureStatementFactory objects"""

import threading

from abc import abstractmethod, ABC
from typing import cast, Dict, List, Type as TypeOf, Union, TYPE_CHECKING
from weakref import ref

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Element import Element

from SimpleSchema.Schema.Elements.Statements.StructureStatement import StructureStatement

from SimpleSchema.Schema.Elements.Types.AliasType import AliasType
from SimpleSchema.Schema.Elements.Types.FundamentalType import FundamentalType
from SimpleSchema.Schema.Elements.Types.TupleType import TupleType
from SimpleSchema.Schema.Elements.Types.Type import Type

from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseItemStatement import ParseItemStatement
from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseStructureStatement import ParseStructureStatement

from SimpleSchema.Schema.Parse.TypeResolver.TypeConversionKey import TypeConversionKey

if TYPE_CHECKING:
    from SimpleSchema.Schema.Parse.TypeResolver.Namespaces import Namespace


# ----------------------------------------------------------------------
class _ElementFactory(ABC):
    """Abstract base class for all element factories"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        desc: str,
        statement: Union[ParseItemStatement, ParseStructureStatement],
        active_namespace: "Namespace",
    ):
        self._desc                          = desc
        self._statement                     = statement
        self._active_namespace_ref          = ref(active_namespace)

        self._created_element: Union[
            None,
            Exception,
            Element,
        ]                                   = None

        self._created_element_lock          = threading.RLock()

    # ----------------------------------------------------------------------
    @property
    def statement(self) -> Union[ParseItemStatement, ParseStructureStatement]:
        return self._statement

    @property
    def active_namespace(self) -> "Namespace":
        active_namespace = self._active_namespace_ref()
        assert active_namespace is not None

        return active_namespace

    # ----------------------------------------------------------------------
    def Create(
        self,
        ancestors: List[TypeConversionKey],
        fundamental_types: Dict[str, TypeOf[FundamentalType]],
    ) -> Element:
        with self._created_element_lock:
            if self._created_element is None:
                try:
                    result = self._CreateImpl(ancestors, fundamental_types)
                except Exception as ex:
                    result = ex

                self._created_element = result

            if isinstance(self._created_element, Exception):
                raise self._created_element

            elif isinstance(self._created_element, Element):
                return self._created_element

            else:
                assert False, self._created_element  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    def Finalize(self) -> None:
        """Finalizes the creation of the type"""
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @abstractmethod
    def _CreateImpl(
        self,
        ancestors: List[TypeConversionKey],
        fundamental_types: Dict[str, TypeOf[FundamentalType]],
    ) -> Element:
        raise Exception("Abstract method")  # pragma: no cover



# ----------------------------------------------------------------------
class AliasTypeFactory(_ElementFactory):
    """Creates an AliasType element"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(AliasTypeFactory, self).__init__("alias type", *args, **kwargs)

    # ----------------------------------------------------------------------
    @property
    def statement(self) -> ParseItemStatement:
        return cast(ParseItemStatement, super(AliasTypeFactory, self).statement)

    # ----------------------------------------------------------------------
    @overridemethod
    def Finalize(self) -> None:
        # Nothing to do here
        pass

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _CreateImpl(
        self,
        ancestors: List[TypeConversionKey],
        fundamental_types: Dict[str, TypeOf[FundamentalType]],
    ) -> AliasType:
        statement = self.statement

        return AliasType(
            statement.range,
            Cardinality(statement.range, None, None, None),
            None,
            statement.name,
            self.active_namespace.ParseTypeToType(
                statement.type,
                TypeConversionKey(statement.name.id.value, statement.range),
                ancestors,
                fundamental_types,
            ),
        )


# ----------------------------------------------------------------------
class StructureStatementFactory(_ElementFactory):
    """Creates a StructureStatement element"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(StructureStatementFactory, self).__init__("structure statement", *args, **kwargs)

    # ----------------------------------------------------------------------
    @property
    def statement(self) -> ParseStructureStatement:
        return cast(ParseStructureStatement, super(StructureStatementFactory, self).statement)

    # ----------------------------------------------------------------------
    def Finalize(self) -> None:
        if isinstance(self._created_element, str):
            return

        assert isinstance(self._created_element, StructureStatement), self._created_element

        for child in self.statement.children:
            if child.is_disabled:
                continue

            self._created_element.children.append(child)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _CreateImpl(
        self,
        ancestors: List[TypeConversionKey],
        fundamental_types: Dict[str, TypeOf[FundamentalType]],
    ) -> StructureStatement:
        statement = self.statement

        bases: List[Type] = []

        if statement.base is not None:
            new_type = self.active_namespace.ParseTypeToType(
                statement.base,
                TypeConversionKey.FromIdentifier(statement.name),
                ancestors,
                fundamental_types,
            )

            if isinstance(new_type, TupleType):
                bases += new_type.types
            else:
                bases.append(new_type)

        return StructureStatement(
            statement.range,
            statement.name,
            bases,
            statement.metadata,
            [], # Statements are added during finalization
        )
