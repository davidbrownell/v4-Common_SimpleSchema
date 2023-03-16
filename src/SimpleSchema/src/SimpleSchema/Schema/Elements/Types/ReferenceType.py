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
from ..Common.Visibility import Visibility, VisibilityTrait

from ..Expressions.Expression import Expression
from ..Expressions.ListExpression import ListExpression
from ..Expressions.NoneExpression import NoneExpression

from ..Types.StructureType import StructureType
from ..Types.VariantType import VariantType

from ....Common import Errors
from ....Common.Range import Range
from ....Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ReferenceType(VisibilityTrait, BaseType):
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

        BasicRefWithCardinality             = auto()
        StructureRefWithCardinality         = auto()

        _ReferencedTypeDelimiter            = auto()

        # Access
        SingleAccess                        = auto()
        SharedAccess                        = auto()

        _AccessDelimiter                    = auto()

        # Miscellaneous
        DynamicallyGenerated                = auto()    # Type generated from code whose range should not participate in exception call stacks
        TypeDefinition                      = auto()    # Type is part of a type definition and should be generated inline by most plugins

        # ----------------------------------------------------------------------
        # |  Amalgamations
        # ----------------------------------------------------------------------

        # Masks
        ReferenceCategoryMask               = _ReferenceCategoryDelimiter - 1
        ReferencedTypeMask                  = (_ReferencedTypeDelimiter - 1) & ~(ReferenceCategoryMask)
        AccessMask                          = (_AccessDelimiter - 1) & ~(ReferenceCategoryMask | ReferencedTypeMask)

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                 = "Reference"

    type: Union[BasicType, "ReferenceType"]
    name: SimpleElement[str]
    cardinality: Cardinality

    _metadata: Union[
        Optional[Metadata],                 # Before ResolveMetadata is called
        dict[
            str,
            Union[
                SimpleElement,              # Metadata item that was recognized and resolved
                Expression,                 # Metadata item that was not recognized and therefore not resolved
            ]
        ],                                  # After ResolveMetadata is called
    ]

    flags: Flag                                         = field(init=False)

    # Indicates that the cardinality should be used to create a new type rather than
    # considering the type to be an alias.
    force_single_cardinality: InitVar[bool]             = field(kw_only=True)

    # Indicates that the type was created via code; the range for this type will not be
    # included in exception stacks.
    was_dynamically_generated: InitVar[bool]            = field(kw_only=True)

    # Indicates that this reference was created as part of the definition of a larger type.
    # Some plugins will use this information to determine if the content associated with
    # the reference type should be generated along with this type or rather as a
    # reference/pointer to a type defined elsewhere.
    is_type_definition: InitVar[bool]                   = field(kw_only=True)

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        visibility: SimpleElement[Visibility],
        name: SimpleElement[str],
        the_type: Union[BasicType, "ReferenceType"],
        cardinality: Cardinality,
        metadata: Optional[Metadata],
        *,
        was_dynamically_generated: bool=False,
        is_type_definition: bool=False,
        range_value: Optional[Range]=None,
    ) -> "ReferenceType":
        if metadata and not metadata.items:
            metadata = None

        if range_value is None:
            range_value = the_type.range

        if isinstance(the_type, BasicType):
            is_type_definition = True

            if cardinality.is_single:
                referenced_type = the_type
            else:
                referenced_type = cls(
                    range_value,
                    SimpleElement[Visibility](the_type.range, Visibility.Private),
                    the_type,
                    SimpleElement[str](
                        the_type.range,
                        "_{}-Item-Ln{}".format(name.value, the_type.range.begin.line),
                    ),
                    Cardinality(the_type.range, None, None),
                    None,
                    force_single_cardinality=True,
                    was_dynamically_generated=was_dynamically_generated,
                    is_type_definition=is_type_definition,
                )
        else:
            referenced_type = the_type

        return cls(
            range_value,
            visibility,
            referenced_type,
            name,
            cardinality,
            metadata,
            force_single_cardinality=False,
            was_dynamically_generated=was_dynamically_generated,
            is_type_definition=is_type_definition,
        )

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        force_single_cardinality: bool,
        was_dynamically_generated: bool,
        is_type_definition: bool,
    ):
        super(ReferenceType, self).__post_init__()

        assert force_single_cardinality is False or self.cardinality.is_single

        # Assume single access until we know otherwise
        flags = 0

        if was_dynamically_generated:
            assert (
                self.visibility.value == Visibility.Private
                and (self.range.begin.line == self.range.begin.column == self.range.end.line == self.range.end.column)
            )

            flags |= ReferenceType.Flag.DynamicallyGenerated

        if is_type_definition:
            flags |= ReferenceType.Flag.TypeDefinition

        # Reference Category
        if (
            force_single_cardinality
            or not self.cardinality.is_single
        ):
            flags |= ReferenceType.Flag.Type

            if self.cardinality.is_optional and isinstance(self.type, ReferenceType):
                with self.type.Resolve() as resolved_type:
                    if resolved_type.cardinality.is_optional:
                        raise Errors.ReferenceTypeOptionalToOptional.Create(self.range)

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

            if self.type.flags & ReferenceType.Flag.BasicRef:
                flags |= ReferenceType.Flag.BasicRefWithCardinality

                if self.type.flags & ReferenceType.Flag.StructureRef:
                    flags |= ReferenceType.Flag.StructureRefWithCardinality

        else:
            assert False, self.type  # pragma: no cover

        object.__setattr__(self, "flags", flags)

    # ----------------------------------------------------------------------
    @property
    def is_metadata_resolved(self) -> bool:
        return isinstance(self._metadata, dict)

    @property
    def unresolved_metadata(self) -> Optional[Metadata]:
        # Valid before ResolveMetadata is called
        assert not isinstance(self._metadata, dict)
        return self._metadata

    @property
    def resolved_metadata(self) -> dict[str, Union[SimpleElement, Expression]]:
        # Valid after ResolveMetadata is called
        assert isinstance(self._metadata, dict)
        return self._metadata

    # ----------------------------------------------------------------------
    def ResolveMetadata(
        self,
        metadata: dict[str, Union[SimpleElement, Expression]],
    ) -> None:
        assert not isinstance(self._metadata, dict)
        object.__setattr__(self, "_metadata", metadata)

    # ----------------------------------------------------------------------
    def ResolveShared(
        self,
        *,
        is_shared: bool,
    ) -> None:
        assert self.flags & ReferenceType.Flag.AccessMask == 0

        flags = self.flags | (
            ReferenceType.Flag.SharedAccess if is_shared else ReferenceType.Flag.SingleAccess
        )

        object.__setattr__(self, "flags", flags)

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
            # Do not include redundant ranges in the exception if the type has been dynamically
            # generated
            if not self.flags & ReferenceType.Flag.DynamicallyGenerated and self.range not in ex.ranges:
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
        yield from VisibilityTrait._GenerateAcceptDetails(self)

        yield "type", cast(WeakReferenceType[Element], ref(self.type))
        yield "name", self.name
        yield "cardinality", self.cardinality

        if isinstance(self._metadata, Metadata):
            yield "metadata", self._metadata
