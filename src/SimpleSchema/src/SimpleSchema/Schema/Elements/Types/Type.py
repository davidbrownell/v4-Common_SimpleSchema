# ----------------------------------------------------------------------
# |
# |  Type.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 11:38:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Type object"""

from abc import abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field, fields, Field, MISSING
from functools import cached_property
from types import NoneType
from typing import Any, Callable, ClassVar, Iterator, Optional, Tuple, Type as PythonType, Union

from Common_Foundation.Types import DoesNotExist, extensionmethod, overridemethod

from ..Common.Cardinality import Cardinality
from ..Common.Element import Element
from ..Common.Metadata import Metadata, MetadataItem

from ..Expressions.Expression import Expression
from ..Expressions.ListExpression import ListExpression
from ..Expressions.NoneExpression import NoneExpression

from ....Common import Errors
from ....Common.Range import Range
from ....Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Type(Element):
    """Abstract base class for types supported by SimpleSchema"""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                                                     = DoesNotExist.instance  # type: ignore
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = DoesNotExist.instance  # type: ignore

    FIELDS: ClassVar[dict[str, Field]]      = field(init=False)

    cardinality: Cardinality
    metadata: Optional[Metadata]

    _single_item_type: Optional["Type"]     = field(init=False)

    # ----------------------------------------------------------------------
    @classmethod
    def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
        assert cls.NAME != DoesNotExist.instance, "Make sure to define the type's name."
        assert cls.SUPPORTED_PYTHON_TYPES != DoesNotExist.instance, "Make sure to define the supported python types."

        cls.__initialize_fields__()
        return super(Type, cls).__new__(cls)

    # ----------------------------------------------------------------------
    @classmethod
    def CreateFromMetadata(
        cls,
        range_value: Range,
        cardinality: Cardinality,
        metadata: Optional[Metadata],
    ) -> "Type":
        cls.__initialize_fields__()

        return cls._CreateTypeInstance(
            range_value,
            cardinality,
            metadata,
            lambda field_name: DoesNotExist.instance,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if self.cardinality.is_container is True:
            single_item_type = self.Clone(Range.CreateFromCode(), Cardinality.CreateFromCode())
        else:
            single_item_type = None

        object.__setattr__(self, "_single_item_type", single_item_type)

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def Resolve(self) -> Iterator["Type"]:
        try:
            yield self
        except SimpleSchemaException as ex:
            ex.ranges.append(self.range)
            raise

    # ----------------------------------------------------------------------
    @cached_property
    def display_name(self) -> str:
        return "{}{}".format(self._display_name, self.cardinality)

    # ----------------------------------------------------------------------
    def DeriveType(
        self,
        range_value: Range,
        cardinality: Cardinality,
        metadata: Metadata,
    ) -> "Type":
        """Return a new type that is derived from this type"""

        return self.__class__._CreateTypeInstance(  # pylint: disable=protected-access
            range_value,
            cardinality,
            metadata,
            lambda field_name: getattr(self, field_name),
        )

    # ----------------------------------------------------------------------
    @extensionmethod
    def Clone(
        self,
        range_value: Range,
        cardinality: Cardinality,
    ) -> "Type":
        """Return the same type with a different cardinality"""

        return self.__class__._CreateTypeInstance(  # pylint: disable=protected-access
            range_value,
            cardinality,
            self.metadata,
            lambda field_name: getattr(self, field_name),
        )

    # ----------------------------------------------------------------------
    @extensionmethod
    def ToPython(
        self,
        expression_or_value: Union[Expression, Any],
    ) -> Any:
        self.cardinality.Validate(expression_or_value)

        if isinstance(expression_or_value, (NoneExpression, NoneType)):
            return None

        if isinstance(expression_or_value, ListExpression):
            try:
                return [self.ItemToPython(item) for item in expression_or_value.value]

            # This clause is only hit right now for tuples, which makes it difficult to unit test
            # within Type_UnitTest.py without recreating the tuple infrastructure there. Rather
            # than doing that, I've eliminated code coverage for these lines and ensured that
            # the scenario is covered in TupleType_UnitTest.py
            except SimpleSchemaException as ex:                             # pragma: no cover
                ex.ranges.append(expression_or_value.range)                 # pragma: no cover
                raise                                                       # pragma: no cover

        elif isinstance(expression_or_value, list):
            return [self.ItemToPython(item) for item in expression_or_value]

        return self.ItemToPython(expression_or_value)

    # ----------------------------------------------------------------------
    @extensionmethod
    def ItemToPython(
        self,
        expression_or_value: Union[Expression, Any],
    ) -> Any:
        # ----------------------------------------------------------------------
        def Impl(
            value: Any,
        ) -> Any:
            if not isinstance(value, self.SUPPORTED_PYTHON_TYPES):  # pylint: disable=isinstance-second-argument-not-valid-type
                raise Exception(
                    Errors.type_validate_invalid_python_type.format(
                        python_type=type(value).__name__,
                        type=self.display_name,
                    ),
                )

            return self._ItemToPythonImpl(value)

        # ----------------------------------------------------------------------

        if isinstance(expression_or_value, Expression):
            try:
                return Impl(expression_or_value.value)
            except Exception as ex:
                raise SimpleSchemaException(expression_or_value.range, str(ex)) from ex

        return Impl(expression_or_value)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @classmethod
    def __initialize_fields__(cls):
        if hasattr(cls, "FIELDS"):
            return

        type_fields: dict[str, Field] = {
                type_field.name: type_field
                for type_field in fields(Type)
                if type_field.init
            }

        class_fields: dict[str, Field] = {
            class_field.name: class_field
            for class_field in fields(cls)
            if class_field.init and class_field.name not in type_fields
        }

        cls.FIELDS = class_fields

    # ----------------------------------------------------------------------
    @classmethod
    def _CreateTypeInstance(
        cls,
        range_value: Range,
        cardinality: Cardinality,
        metadata: Optional[Metadata],
        on_missing_metadata_func: Callable[[str], Union[DoesNotExist, Any]],
    ) -> "Type":
        if metadata is None:
            pop_metadata_item_func = lambda name: DoesNotExist.instance
        else:
            pop_metadata_item_func = lambda name: metadata.items.pop(name, DoesNotExist.instance)

        construct_args: dict[str, Any] = {
            "range": range_value,
            "cardinality": cardinality,
            "metadata": metadata,
        }

        for class_field in cls.FIELDS.values():
            assert class_field.name not in construct_args, class_field.name

            metadata_item = pop_metadata_item_func(class_field.name)

            if isinstance(metadata_item, DoesNotExist):
                metadata_value = on_missing_metadata_func(class_field.name)
                if isinstance(metadata_value, DoesNotExist):
                    continue
            else:
                assert isinstance(metadata_item, MetadataItem), metadata_item

                # Note that this content is imported here to avoid circular dependencies
                from .FundamentalTypes.Impl.CreateTypeFromAnnotation import CreateTypeFromAnnotation

                metadata_value = CreateTypeFromAnnotation(
                    class_field.type,
                    has_default_value=class_field.default is not MISSING or class_field.default_factory is not MISSING,
                ).ToPython(metadata_item.expression)

            if (
                metadata_value is not None
                or (class_field.default is MISSING and class_field.default_factory is MISSING)
            ):
                construct_args[class_field.name] = metadata_value

        if metadata is not None and not metadata.items:
            construct_args["metadata"] = None

        try:
            return cls(**construct_args)
        except Exception as ex:
            raise SimpleSchemaException(
                metadata.range if metadata is not None else range_value,
                str(ex),
            ) from ex

    # ----------------------------------------------------------------------
    @extensionmethod
    @property
    def _display_name(self) -> str:
        return self.NAME

    # ----------------------------------------------------------------------
    @overridemethod
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsGeneratorType:  # pragma: no cover
        yield "cardinality", self.cardinality

        if self.metadata:
            yield "metadata", self.metadata

    # ----------------------------------------------------------------------
    @abstractmethod
    def _ItemToPythonImpl(
        self,
        value: Any,
    ) -> Any:
        raise Exception("Abstract method")  # pragma: no cover
