# ----------------------------------------------------------------------
# |
# |  ReferenceType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-04-01 09:37:40
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
from enum import auto, Enum
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

from ..Types.BasicType import BasicType
from ..Types.VariantType import VariantType

from ....Common import Errors
from ....Common.Range import Range
from ....Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ReferenceType(VisibilityTrait, BaseType):
    """A type that references another type, but adds specific cardinality and/or metadata"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class Category(Enum):
        Source                              = auto()    # Reference wrapper for the original source
        Reference                           = auto()    # References the type in the creation of a new type (perhaps a container or optional)
        Alias                               = auto()    # The reference's cardinality value is the same as the type that it references

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                     = "Reference"

    type: Union[BasicType, "ReferenceType"]
    name: SimpleElement[str]

    cardinality: Cardinality

    _metadata: Union[
        Optional[Metadata],                 # Valid before `ResolveMetadata` is called
        dict[                               # Valid after `ResolveMetadata` is called
            str,
            Union[
                SimpleElement,              # Metadata item that was recognized and resolved
                Expression,                 # Metadata item that was not recognized and therefore not resolved
            ],
        ],
    ]

    category: Category                      = field(init=False)

    # Valid after `ResolvedIsShared` is called
    _is_shared: Optional[bool]              = field(init=False, default=None)

    is_source: InitVar[bool]                = field(kw_only=True, default=False)

    # Indicate that is reference's range should not be added in the exceptions range stack.
    # This will generally be used when the type associated with the reference were dynamically
    # created in code and will not be meaningful to the caller.
    suppress_range_in_exceptions: bool      = field(kw_only=True, default=False)

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
        range_value: Optional[Range]=None,
        suppress_range_in_exceptions: bool=False,
    ) -> "ReferenceType":
        if metadata and not metadata.items:
            metadata = None

        if range_value is None:
            range_value = the_type.range

        if isinstance(the_type, BasicType):
            is_source = True

            if cardinality.is_single:
                referenced_type = the_type
                assert is_source

            else:
                referenced_type = cls(
                    range_value,
                    SimpleElement[Visibility](the_type.range, Visibility.Private),
                    the_type,
                    SimpleElement[str](
                        the_type.range,
                        "{}-Item-Ln{}Col{}".format(
                            name.value,
                            the_type.range.begin.line,
                            the_type.range.begin.column,
                        ),
                    ),
                    Cardinality(the_type.range, None, None),
                    None,
                    is_source=True,
                    suppress_range_in_exceptions=suppress_range_in_exceptions,
                )
        else:
            is_source = False

            referenced_type = the_type

        return cls(
            range_value,
            visibility,
            referenced_type,
            name,
            cardinality,
            metadata,
            is_source=is_source,
            suppress_range_in_exceptions=suppress_range_in_exceptions,
        )

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        is_source: bool,
    ):
        super(ReferenceType, self).__post_init__()

        # Category
        if is_source:
            category = ReferenceType.Category.Source

        elif self.cardinality.is_single:
            category = ReferenceType.Category.Alias

            if isinstance(self.type, ReferenceType):
                object.__setattr__(self, "cardinality", self.type.cardinality)

        else:
            category = ReferenceType.Category.Reference

            if self.cardinality.is_optional and isinstance(self.type, ReferenceType):
                with self.type.Resolve() as resolved_type:
                    if resolved_type.cardinality.is_optional:
                        raise Errors.ReferenceTypeOptionalToOptional.Create(self.cardinality.range)

        object.__setattr__(self, "category", category)

    # ----------------------------------------------------------------------
    @property
    def is_metadata_resolved(self) -> bool:
        return isinstance(self._metadata, dict)

    @property
    def unresolved_metadata(self) -> Optional[Metadata]:
        if isinstance(self._metadata, dict):
            raise RuntimeError("Metadata has been resolved.")

        return self._metadata

    @property
    def resolved_metadata(self) -> dict[str, Union[SimpleElement, Expression]]:
        if self._metadata is None or isinstance(self._metadata, Metadata):
            raise RuntimeError("Metadata has not yet been resolved.")

        return self._metadata

    # ----------------------------------------------------------------------
    def ResolveMetadata(
        self,
        metadata: dict[str, Union[SimpleElement, Expression]],
    ) -> None:
        if self.is_metadata_resolved:
            raise RuntimeError("Metadata has already been resolved.")

        object.__setattr__(self, "_metadata", metadata)

    # ----------------------------------------------------------------------
    @property
    def is_shared_resolved(self) -> bool:
        return self._is_shared is not None

    @property
    def is_shared(self) -> bool:
        if self._is_shared is None:
            raise RuntimeError("Shared status has not been resolved.")

        return self._is_shared

    # ----------------------------------------------------------------------
    def ResolveIsShared(
        self,
        is_shared: bool,
    ) -> None:
        if self.is_shared_resolved:
            raise RuntimeError("Shared status has already been resolved.")

        object.__setattr__(self, "_is_shared", is_shared)

    # ----------------------------------------------------------------------
    @contextmanager
    def Resolve(self) -> Iterator["ReferenceType"]:
        try:
            if self.category != ReferenceType.Category.Alias or isinstance(self.type, BasicType):
                yield self
                return

            assert isinstance(self.type, ReferenceType), self.type
            with self.type.Resolve() as resolved_type:
                yield resolved_type

        except SimpleSchemaException as ex:
            if not self.suppress_range_in_exceptions and self.range not in ex.ranges:
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
        if isinstance(expression_or_value, (NoneExpression, NoneType)):
            self.cardinality.Validate(expression_or_value)
            return None

        if self.cardinality.is_optional:
            return self.type.ToPython(expression_or_value)

        with self.Resolve() as resolved_type:
            # Variants are special in that the subtypes may be collections or individual types.
            # If we are looking at a Variant, let it handle the cardinality stuff using its
            # own custom logic.
            if isinstance(resolved_type.type, VariantType):
                return resolved_type.type.ToPythonReferenceOverride(
                    resolved_type,
                    expression_or_value,
                )

            return resolved_type.ToPythonImpl(expression_or_value)

    # ----------------------------------------------------------------------
    def ToPythonImpl(
        self,
        expression_or_value: Union[Expression, Any],
    ) -> Any:
        # This function is called during normal operations or when a VariantType has
        # determined that special cardinality rules are not in play.
        assert not isinstance(expression_or_value, (NoneExpression, NoneType))

        self.cardinality.Validate(expression_or_value)

        items: Optional[list] = None

        if isinstance(expression_or_value, ListExpression):
            items = expression_or_value.value
        elif isinstance(expression_or_value, list):
            items = expression_or_value

        if items is not None:
            return [self.type.ToPython(item) for item in items]

        return self.type.ToPython(expression_or_value)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @property
    @overridemethod
    def _display_type(self) -> str:
        display = self.type.display_type

        if not self.cardinality.is_single and display.endswith("}"):
            display = "<{}>".format(display)

        if self.category != ReferenceType.Category.Alias:
            display = "{}{}".format(display, self.cardinality)

        return display

    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield from VisibilityTrait._GenerateAcceptDetails(self)

        yield "name", self.name
        yield "cardinality", self.cardinality

        if isinstance(self._metadata, Metadata):
            yield "metadata", self._metadata

        yield "type", cast(WeakReferenceType[Element], ref(self.type))
