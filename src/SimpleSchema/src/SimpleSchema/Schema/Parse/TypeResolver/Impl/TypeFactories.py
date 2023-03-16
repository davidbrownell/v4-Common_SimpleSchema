# ----------------------------------------------------------------------
# |
# |  TypeFactories.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-13 13:22:24
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ReferenceTypeFactory and StructureTypeFactory objects"""

import threading

from abc import abstractmethod, ABC
from typing import cast, Type as PythonType, Union, TYPE_CHECKING
from weakref import ref, ReferenceType as WeakReferenceType

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation.Types import extensionmethod, overridemethod

from ...ANTLR.Elements.Statements.ParseItemStatement import ParseItemStatement
from ...ANTLR.Elements.Statements.ParseStructureStatement import ParseStructureStatement

from ....Elements.Common.SimpleElement import SimpleElement
from ....Elements.Common.Visibility import Visibility

from ....Elements.Statements.Statement import Statement
from ....Elements.Statements.StructureStatement import StructureStatement

from ....Elements.Types.FundamentalType import FundamentalType
from ....Elements.Types.ReferenceType import ReferenceType
from ....Elements.Types.StructureType import StructureType

from .....Common import Errors

if TYPE_CHECKING:  # pragma: no cover
    from .Namespace import Namespace


# ----------------------------------------------------------------------
class _TypeFactory(ABC):
    """Abstract base class for all type factories"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        statement: Union[ParseItemStatement, ParseStructureStatement],
        active_namespace: "Namespace",
    ):
        self._statement                                                     = statement

        self._active_namespace_ref: WeakReferenceType["Namespace"]          = ref(active_namespace)

        self._created_type: Union[None, Exception, ReferenceType]           = None
        self._created_type_ref_count: int                                   = 0
        self._created_type_lock                                             = threading.RLock()

    # ----------------------------------------------------------------------
    @property
    @extensionmethod
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
        ancestor_identities: list[SimpleElement[str]],
        fundamental_types: dict[str, PythonType[FundamentalType]],
    ) -> ReferenceType:
        with self._created_type_lock:
            if self._created_type is None:
                try:
                    result = self._CreateImpl(ancestor_identities, fundamental_types)

                except Exception as ex:
                    result = ex

                self._created_type = result
            else:
                # We only want to increment the reference count when the type is referenced,
                # not when it is created.
                self._created_type_ref_count += 1

        if isinstance(self._created_type, Exception):
            raise self._created_type

        if isinstance(self._created_type, ReferenceType):
            return self._created_type

        assert False, self._created_type  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    def Finalize(self) -> None:
        """Finalizes the created element"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @abstractmethod
    def _CreateImpl(
        self,
        ancestor_identities: list[SimpleElement[str]],
        fundamental_types: dict[str, PythonType[FundamentalType]],
    ) -> ReferenceType:
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
class StructureTypeFactory(_TypeFactory):
    # ----------------------------------------------------------------------
    @property
    @overridemethod
    def statement(self) -> ParseStructureStatement:
        return cast(ParseStructureStatement, super(StructureTypeFactory, self).statement)

    # ----------------------------------------------------------------------
    @overridemethod
    def Finalize(self) -> None:
        the_type = self._created_type
        assert isinstance(the_type, ReferenceType), the_type

        while isinstance(the_type, ReferenceType):
            the_type = the_type.type

        assert isinstance(the_type, StructureType), the_type

        for child in self.statement.children:
            if child.is_disabled:
                continue

            the_type.structure.children.append(child)  # pylint: disable=no-member

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _CreateImpl(
        self,
        ancestor_identities: list[SimpleElement[str]],
        fundamental_types: dict[str, PythonType[FundamentalType]],
    ) -> ReferenceType:
        statement = self.statement
        active_namespace = self.active_namespace

        base_types: list[ReferenceType] = []

        if statement.bases:
            ancestor_identities.append(statement.name.ToSimpleElement())
            with ExitStack(ancestor_identities.pop):
                for base_index, base in enumerate(statement.bases):
                    base_type = active_namespace.ParseTypeToType(
                        SimpleElement[Visibility](base.range, Visibility.Private),
                        SimpleElement[str](
                            base.range,
                            "_Base{}".format(base_index),
                        ),
                        base,
                        SimpleElement[str](
                            base.range,
                            "Base type '{}' (index {})".format(base.display_type, base_index),
                        ),
                        ancestor_identities,
                        fundamental_types,
                    )

                    with base_type.Resolve() as resolved_base_type:
                        if not resolved_base_type.cardinality.is_single:
                            raise Errors.TypeFactoryInvalidBaseCardinality.Create(
                                base.range,
                            )

                        if (
                            not isinstance(resolved_base_type.type, FundamentalType)
                            and not isinstance(resolved_base_type.type, StructureType)
                        ):
                            raise Errors.TypeFactoryInvalidBaseType.Create(resolved_base_type.range)

                        if len(statement.bases) > 1 and not isinstance(resolved_base_type.type, StructureType):
                            raise Errors.TypeFactoryInvalidBaseTypeMultiInheritance.Create(resolved_base_type.range)

                    base_types.append(base_type)

        result = ReferenceType.Create(
            statement.name.visibility,
            statement.name.ToSimpleElement(),
            StructureType(
                statement.range,
                StructureStatement(
                    statement.range,
                    SimpleElement[str](
                        statement.range,
                        "_{}-Struct-Ln{}".format(statement.name.value, statement.range.begin.line),
                    ),
                    base_types,  # type: ignore
                    [], # The children will be populated during Finalize
                ),  # type: ignore
            ),
            statement.cardinality,
            statement.unresolved_metadata,
            is_type_definition=True,
        )

        return result


# ----------------------------------------------------------------------
class ReferenceTypeFactory(_TypeFactory):
    # ----------------------------------------------------------------------
    @property
    @overridemethod
    def statement(self) -> ParseItemStatement:
        return cast(ParseItemStatement, super(ReferenceTypeFactory, self).statement)

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
        ancestor_identities: list[SimpleElement[str]],
        fundamental_types: dict[str, PythonType[FundamentalType]],
    ) -> ReferenceType:
        statement = self.statement

        name_element = statement.name.ToSimpleElement()

        return self.active_namespace.ParseTypeToType(
            statement.name.visibility,
            name_element,
            statement.type,
            name_element,
            ancestor_identities,
            fundamental_types,
            range_value=statement.range,
        )
