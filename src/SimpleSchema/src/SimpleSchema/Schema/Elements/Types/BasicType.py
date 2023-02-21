# ----------------------------------------------------------------------
# |
# |  BasicType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-13 11:11:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BasicType object"""

from abc import abstractmethod
from dataclasses import dataclass, field, fields, Field, MISSING
from typing import Any, Callable, ClassVar, Optional, Tuple, Type as PythonType, Union

from Common_Foundation.Types import DoesNotExist, overridemethod

from .Impl.BaseType import BaseType

from ..Common.Metadata import Metadata, MetadataItem

from ..Expressions.Expression import Expression

from ....Common import Errors
from ....Common.Range import Range
from ....Common.SimpleSchemaException import SimpleSchemaException


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class BasicType(BaseType):
    """A type that does not have cardinality or metadata"""

    # ----------------------------------------------------------------------
    SUPPORTED_PYTHON_TYPES: ClassVar[Tuple[PythonType, ...]]                = DoesNotExist.instance  # type: ignore

    FIELDS: ClassVar[dict[str, Field]]                                      = field(init=False)

    # ----------------------------------------------------------------------
    @classmethod
    def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
        assert cls.SUPPORTED_PYTHON_TYPES != DoesNotExist.instance, "Make sure the define the supported python types."

        cls.__initialize_fields__()
        return super(BasicType, cls).__new__(cls)

    # ----------------------------------------------------------------------
    @classmethod
    def __initialize_fields__(cls):
        if hasattr(cls, "FIELDS"):
            return

        basic_type_fields: dict[str, Field] = {
            type_field.name: type_field
            for type_field in fields(BasicType)
            if type_field.init
        }

        class_fields: dict[str, Field] = {
            class_field.name: class_field
            for class_field in fields(cls)
            if class_field.init and class_field.name not in basic_type_fields
        }

        cls.FIELDS = class_fields

    # ----------------------------------------------------------------------
    @classmethod
    def CreateFromMetadata(
        cls,
        range_value: Range,
        metadata: Optional[Metadata],
    ) -> "BasicType":
        cls.__initialize_fields__()

        return cls._Create(
            range_value,
            metadata,
            lambda field_name: DoesNotExist.instance,
        )

    # ----------------------------------------------------------------------
    def DeriveNewType(
        self,
        range_value: Range,
        metadata: Metadata,
    ) -> "BasicType":
        return self.__class__._Create(  # pylint: disable=protected-access
            range_value,
            metadata,
            lambda field_name: getattr(self, field_name),
        )

    # ----------------------------------------------------------------------
    @overridemethod
    def ToPython(
        self,
        expression_or_value: Union[Expression, Any],
    ) -> Any:
        # ----------------------------------------------------------------------
        def Impl(
            value: Any,
        ) -> Any:
            if not isinstance(value, self.SUPPORTED_PYTHON_TYPES):  # pylint: disable=isinstance-second-argument-not-valid-type
                raise Exception(
                    Errors.basic_type_validate_invalid_python_type.format(
                        python_type=type(value).__name__,
                        type=self.display_type,
                    ),
                )

            return self._ToPythonImpl(value)

        # ----------------------------------------------------------------------

        if isinstance(expression_or_value, Expression):
            try:
                return Impl(expression_or_value.value)

            except SimpleSchemaException as ex:
                ex.ranges.append(expression_or_value.range)
                raise

            except Exception as ex:
                raise SimpleSchemaException(expression_or_value.range, str(ex)) from ex

        return Impl(expression_or_value)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @classmethod
    def _Create(
        cls,
        range_value: Range,
        metadata: Optional[Metadata],
        on_missing_metadata_func: Callable[[str], Union[DoesNotExist, Any]],
    ) -> "BasicType":
        if metadata is None:
            pop_metadata_item_func = lambda name: DoesNotExist.instance
        else:
            pop_metadata_item_func = lambda name: metadata.items.pop(name, DoesNotExist.instance)

        construct_args: dict[str, Any] = {
            "range": range_value,
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

                metadata_type = CreateTypeFromAnnotation(
                    class_field.type,
                    has_default_value=class_field.default is not MISSING or class_field.default_factory is not MISSING,
                )

                metadata_value = metadata_type.ToPython(metadata_item.expression)

            if (
                metadata_value is not None
                or (class_field.default is MISSING and class_field.default_factory is MISSING)
            ):
                construct_args[class_field.name] = metadata_value

        try:
            return cls(**construct_args)

        except SimpleSchemaException as ex:
            ex.ranges.append(metadata.range if metadata is not None else range_value)
            raise

        except Exception as ex:
            raise SimpleSchemaException(
                metadata.range if metadata is not None else range_value,
                str(ex),
            ) from ex

    # ----------------------------------------------------------------------
    @abstractmethod
    def _ToPythonImpl(
        self,
        value: Any,
    ) -> Any:
        raise Exception("Abstract method")  # pragma: no cover
