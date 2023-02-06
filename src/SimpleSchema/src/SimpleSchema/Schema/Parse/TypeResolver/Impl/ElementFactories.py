# ----------------------------------------------------------------------
# |
# |  ElementFactories.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 09:47:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypedefTypeFactory and StructureStatementFactory objects"""

import threading

from abc import abstractmethod, ABC
from typing import cast, Type as TypeOf, Union, TYPE_CHECKING
from weakref import ref, ReferenceType

from Common_Foundation.Types import overridemethod

from ...ANTLR.Elements.Statements.ParseItemStatement import ParseItemStatement
from ...ANTLR.Elements.Statements.ParseStructureStatement import ParseStructureStatement

from ....Elements.Common.Cardinality import Cardinality
from ....Elements.Common.Element import Element
from ....Elements.Common.SimpleElement import SimpleElement

from ....Elements.Statements.Statement import Statement
from ....Elements.Statements.StructureStatement import StructureStatement

from ....Elements.Types.FundamentalType import FundamentalType
from ....Elements.Types.Type import Type
from ....Elements.Types.TypedefType import TypedefType

if TYPE_CHECKING:  # pragma: no cover
    from .Namespace import Namespace


# ----------------------------------------------------------------------
class _ElementFactory(ABC):
    """Abstract base class for all element factories"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        statement: Union[ParseItemStatement, ParseStructureStatement],
        active_namespace: "Namespace",
    ):
        self._statement                     = statement

        self._active_namespace_ref: ReferenceType["Namespace"]              = ref(active_namespace)

        self._created_element: Union[
            None,
            Exception,
            Element,
        ]                                   = None

        self._created_element_lock          = threading.RLock()

    # ----------------------------------------------------------------------
    @property
    def statement(self) -> Statement:
        return self._statement

    @property
    def active_namespace(self) -> "Namespace":
        active_namespace = self._active_namespace_ref()
        assert active_namespace is not None

        return active_namespace

    # ----------------------------------------------------------------------
    def GetOrCreate(
        self,
        ancestors: list[SimpleElement[str]],
        fundamental_types: dict[str, TypeOf[FundamentalType]],
    ) -> Element:
        with self._created_element_lock:
            if self._created_element is None:
                try:
                    result = self._Create(ancestors, fundamental_types)
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
        """Finalizes the created element"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @abstractmethod
    def _Create(
        self,
        ancestors: list[SimpleElement[str]],
        fundamental_types: dict[str, TypeOf[FundamentalType]],
    ) -> Element:
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
class StructureStatementFactory(_ElementFactory):
    """Creates a StructureStatement element"""

    # ----------------------------------------------------------------------
    @property
    def statement(self) -> ParseStructureStatement:
        return cast(ParseStructureStatement, super(StructureStatementFactory, self).statement)

    # ----------------------------------------------------------------------
    @overridemethod
    def Finalize(self) -> None:
        assert isinstance(self._created_element, StructureStatement), self._created_element

        for child in self.statement.children:
            if child.is_disabled:
                continue

            self._created_element.children.append(child)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _Create(
        self,
        ancestors: list[SimpleElement[str]],
        fundamental_types: dict[str, TypeOf[FundamentalType]],
    ) -> StructureStatement:
        statement = self.statement

        statement_name = statement.name.ToSimpleElement()

        base_types: list[Type] = []

        for base in (statement.bases or []):
            base_types.append(
                self.active_namespace.ParseTypeToType(
                    base,
                    statement_name,
                    ancestors,
                    fundamental_types,
                ),
            )

        return StructureStatement(
            statement.range,
            statement.name.visibility,
            statement_name,
            base_types,
            statement.metadata,
            [], # Statements are added during finalization
        )


# ----------------------------------------------------------------------
class TypedefTypeFactory(_ElementFactory):
    """Creates a TypedefType element"""

    # ----------------------------------------------------------------------
    @property
    def statement(self) -> ParseItemStatement:
        return cast(ParseItemStatement, super(TypedefTypeFactory, self).statement)

    # ----------------------------------------------------------------------
    @overridemethod
    def Finalize(self) -> None:
        # Nothing to do here
        pass

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _Create(
        self,
        ancestors: list[SimpleElement[str]],
        fundamental_types: dict[str, TypeOf[FundamentalType]],
    ) -> TypedefType:
        statement = self.statement

        resolved_type = self.active_namespace.ParseTypeToType(
            statement.type,
            statement.name.ToSimpleElement(),
            ancestors,
            fundamental_types,
        )

        metadata = statement.type.metadata

        if metadata is not None and not metadata.items:
            metadata = None

        return TypedefType(
            statement.range,
            Cardinality(statement.range, None, None, None),
            metadata,
            statement.name.visibility,
            statement.name.ToSimpleElement(),
            resolved_type,
        )
