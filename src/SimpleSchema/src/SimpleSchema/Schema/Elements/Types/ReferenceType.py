# ----------------------------------------------------------------------
# |
# |  ReferenceType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-13 11:44:11
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ReferenceType object"""

from contextlib import contextmanager
from dataclasses import dataclass, field, InitVar
from enum import auto, IntFlag
from types import NoneType
from typing import Any, cast, ClassVar, Iterator, Optional, Union
from weakref import ref, ReferenceType as WeakReferenceType

from Common_Foundation.Types import overridemethod

from .BasicType import BasicType

from .Impl.BaseType import BaseType

from ..Common.Cardinality import Cardinality
from ..Common.Element import Element
from ..Common.Metadata import Metadata
from ..Common.SimpleElement import SimpleElement
from ..Common.Visibility import Visibility

from ..Expressions.Expression import Expression
from ..Expressions.ListExpression import ListExpression
from ..Expressions.NoneExpression import NoneExpression

from ..Types.StructureType import StructureType
from ..Types.VariantType import VariantType

from ....Common.Range import Range
from ....Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ReferenceType(BaseType):
    """A type that has cardinality and metadata"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class Flag(IntFlag):
        # Reference Category
        Type                                = auto()
        Alias                               = auto()

        _ReferenceCategoryDelimiter         = auto()

        # Referenced Type
        BasicRef                            = auto()
        StructureRef                        = auto()
        ReferenceRef                        = auto()

        BasicCollectionRef                  = auto()
        StructureCollectionRef              = auto()

        _ReferencedTypeDelimiter            = auto()

        # Miscellaneous
        DynamicallyGenerated                = auto()

        DefinedInline                        = auto()

        # ----------------------------------------------------------------------
        # |  Amalgamations
        # ----------------------------------------------------------------------

        # Masks
        ReferenceCategoryMask               = _ReferenceCategoryDelimiter - 1
        ReferencedTypeMask                  = (_ReferencedTypeDelimiter - 1) & (~ReferenceCategoryMask)

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                 = "Reference"

    type: Union[BasicType, "ReferenceType"]

    visibility: SimpleElement[Visibility]
    name: SimpleElement[str]

    cardinality: Cardinality
    metadata: Optional[Metadata]

    flags: Flag                                         = field(init=False)

    force_single_cardinality: InitVar[bool]             = field(kw_only=True)
    was_dynamically_generated: InitVar[bool]            = field(kw_only=True)

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        range_value: Range,
        visibility: SimpleElement[Visibility],
        name: SimpleElement[str],
        the_type: Union[BasicType, "ReferenceType"],
        cardinality: Cardinality,
        metadata: Optional[Metadata],
        *,
        was_dynamically_generated: bool=False,
    ) -> "ReferenceType":
        if metadata and not metadata.items:
            metadata = None

        if isinstance(the_type, BasicType):
            if cardinality.is_single:
                referenced_type = the_type
            else:
                referenced_type = cls(
                    range_value,
                    the_type,
                    SimpleElement[Visibility](the_type.range, Visibility.Private),
                    SimpleElement[str](
                        the_type.range,
                        "_{}-Item-Ln{}".format(name.value, the_type.range.begin.line),
                    ),
                    Cardinality(the_type.range, None, None),
                    None,
                    force_single_cardinality=True,
                    was_dynamically_generated=True,
                )
        else:
            referenced_type = the_type

        return cls(
            range_value,
            referenced_type,
            visibility,
            name,
            cardinality,
            metadata,
            force_single_cardinality=False,
            was_dynamically_generated=was_dynamically_generated,
        )

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        force_single_cardinality: bool,
        was_dynamically_generated: bool,
    ):
        super(ReferenceType, self).__post_init__()

        assert force_single_cardinality is False or self.cardinality.is_single
        assert was_dynamically_generated is False or self.visibility.value == Visibility.Private

        flags = 0

        # Reference Category
        if (
            force_single_cardinality
            or not self.cardinality.is_single
        ):
            flags |= ReferenceType.Flag.Type
        else:
            flags |= ReferenceType.Flag.Alias

            if isinstance(self.type, ReferenceType):
                object.__setattr__(self, "cardinality", self.type.cardinality)

        # Reference Type
        if isinstance(self.type, BasicType):
            flags |= ReferenceType.Flag.BasicRef

            if isinstance(self.type, StructureType):
                flags |= ReferenceType.Flag.StructureRef

        elif isinstance(self.type, ReferenceType):
            flags |= ReferenceType.Flag.ReferenceRef

            if self.type.flags & ReferenceType.Flag.DynamicallyGenerated:
                flags |= ReferenceType.Flag.BasicCollectionRef

                if self.type.flags & ReferenceType.Flag.StructureRef:
                    flags |= ReferenceType.Flag.StructureCollectionRef
        else:
            assert False, self.type  # pragma: no cover

        # Miscellaneous
        if was_dynamically_generated:
            flags |= ReferenceType.Flag.DynamicallyGenerated

        # Add a flag that indicates that the type is defined inline
        if (
            # This is a type referencing a BasicType (meaning that it will not be defined externally)
            (flags & ReferenceType.Flag.BasicRef)

            # This is a type referencing a StructureType
            or (
                (flags & ReferenceType.Flag.Type)
                and self.range == self.type.range
            )
        ):
            flags |= ReferenceType.Flag.DefinedInline

        object.__setattr__(self, "flags", flags)

    # ----------------------------------------------------------------------
    @overridemethod
    def Increment(
        self,
        *,
        shallow: bool=False,
    ) -> None:
        super(ReferenceType, self).Increment(shallow=shallow)
        self.type.Increment(shallow=shallow)

    # ----------------------------------------------------------------------
    @contextmanager
    def Resolve(self) -> Iterator["ReferenceType"]:
        try:
            if (
                (self.flags & ReferenceType.Flag.Type)
                or (self.flags & ReferenceType.Flag.BasicRef)
            ):
                yield self
                return

            assert isinstance(self.type, ReferenceType), self.type
            with self.type.Resolve() as resolved_type:  # pylint: disable=no-member
                yield resolved_type

        except SimpleSchemaException as ex:
            if not self.flags & ReferenceType.Flag.DynamicallyGenerated:
                ex.ranges.append(self.range)

            raise

        except Exception as ex:
            raise SimpleSchemaException(self.range, str(ex)) from ex

    # ----------------------------------------------------------------------
    @overridemethod
    def ToPython(
        self,
        expression_or_value: Union[Expression, Any],
    ) -> Any:
        with self.Resolve() as resolved_type:
            if isinstance(expression_or_value, (NoneExpression, NoneType)):
                self.cardinality.Validate(expression_or_value)
                return None

            if self.cardinality.is_optional:
                return self.type.ToPython(expression_or_value)

            if (
                (resolved_type.flags & ReferenceType.Flag.BasicRef)
                and isinstance(resolved_type.type, VariantType)
            ):
                variant_type = cast(VariantType, resolved_type.type)

                return variant_type.ToPythonReferenceOverride(  # pylint: disable=no-member
                    resolved_type,
                    expression_or_value,
                )

            return resolved_type.ToPythonImpl(expression_or_value)

    # ----------------------------------------------------------------------
    def ToPythonImpl(
        self,
        expression_or_value: Union[Expression, Any],
    ) -> Any:
        assert not isinstance(expression_or_value, (NoneExpression, NoneType))

        self.cardinality.Validate(expression_or_value)

        if isinstance(expression_or_value, (ListExpression, list)):
            if isinstance(expression_or_value, ListExpression):
                items = expression_or_value.value
            elif isinstance(expression_or_value, list):
                items = expression_or_value
            else:
                assert False, expression_or_value  # pragma: no cover

            return [self.type.ToPython(item) for item in items]

        return self.type.ToPython(expression_or_value)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @property
    @overridemethod
    def _display_type(self) -> str:
        display = self.type.display_type

        if not self.cardinality.is_single and display.endswith("}"):
            display = "<{}>".format(display)

        if self.flags & ReferenceType.Flag.Type:
            display = "{}{}".format(display, self.cardinality)

        return display

    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "type", cast(WeakReferenceType[Element], ref(self.type))

        yield "visibility", self.visibility
        yield "name", self.name

        yield "cardinality", self.cardinality

        if self.metadata is not None:
            yield "metadata", self.metadata
