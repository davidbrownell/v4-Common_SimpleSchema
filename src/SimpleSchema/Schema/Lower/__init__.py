# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-27 08:58:02
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that lowers/normalizes Elements previously parsed"""

import copy

from contextlib import contextmanager
from dataclasses import dataclass
from typing import List, Optional, Union

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Elements.Types.Type import Type
from SimpleSchema.Schema.Visitors.Visitor import *


# # ----------------------------------------------------------------------
# def Lower(
#     element: RootStatement,
# ) -> RootStatement:
#     visitor = _Visitor()
#
#     element.Accept(visitor)
#
#     return element
#
#
# # ----------------------------------------------------------------------
# # ----------------------------------------------------------------------
# # ----------------------------------------------------------------------
# class _Visitor(object):
#     # ----------------------------------------------------------------------
#     def __init__(self):
#         self._contained_visitor             = Visitor()
#
#         self._pseudo_ctr                    = 0
#         self._stack: List[Element]          = []
#
#     # ----------------------------------------------------------------------
#     @classmethod
#     def IsPseudoType(
#         cls,
#         the_type: Type,
#     ) -> bool:
#         if not isinstance(the_type, IdentifierType):
#             return False
#
#         if len(the_type.identifiers) > 1:
#             return False
#
#         return the_type.identifiers[0].id.value.startswith("_PseudoType")
#
#     # ----------------------------------------------------------------------
#     @overridemethod
#     @contextmanager
#     def OnElement(
#         self,
#         element: Element,  # pylint: disable=unused-argument
#     ) -> Iterator[Optional[VisitResult]]:
#         if self._stack:
#             element.SetParent(self._stack[-1])
#
#         self._stack.append(element)
#         with ExitStack(self._stack.pop):
#             yield VisitResult.Continue
#
#     # ----------------------------------------------------------------------
#     def __getattr__(
#         self,
#         name: str,
#     ):
#         match = self._contained_visitor.DETAILS_REGEX.match(name)
#         if match:
#             return self.__class__._DefaultDetailMethod
#
#         match = self._contained_visitor.METHOD_REGEX.match(name)
#         if match:
#             return self.__class__._DefaultMethod
#
#         raise AttributeError(name)
#
#     # ----------------------------------------------------------------------
#     @contextmanager
#     def OnStructureStatement(
#         self,
#         element: StructureStatement
#     ) -> Iterator[Optional[VisitResult]]:
#         if element.name.is_expression:
#             self._InsertPseudoType(element)
#
#             yield VisitResult.SkipAll
#             return
#
#         yield
#
#     # ----------------------------------------------------------------------
#     @contextmanager
#     def OnItemStatement(
#         self,
#         element: ItemStatement,
#     ) -> Iterator[Optional[VisitResult]]:
#         if (
#             element.name.is_expression
#             and not element.type.cardinality.is_single
#             and not self.__class__.IsPseudoType(element.type)
#         ):
#             self._InsertPseudoType(element)
#
#             yield VisitResult.SkipAll
#             return
#
#         yield
#
#     # ----------------------------------------------------------------------
#     # |
#     # |  Private Types
#     # |
#     # ----------------------------------------------------------------------
#     @dataclass(frozen=True)
#     class _SplitMetadata(object):
#         # ----------------------------------------------------------------------
#         the_type: Optional[Metadata]
#         instance: Optional[Metadata]
#
#         # ----------------------------------------------------------------------
#         @classmethod
#         def Create(
#             cls,
#             metadata: Optional[Metadata],
#         ) -> "_Visitor._SplitMetadata":
#             if metadata is None:
#                 return _Visitor._SplitMetadata(None, None)  # pylint: disable=protected-access
#
#             type_metadata_items: List[MetadataItem] = []
#             instance_metadata_items: List[MetadataItem] = []
##
#             for metadata_item in metadata.items.values():
#                 if metadata_item.name.id.value in [
#                     # CollectionType
#                     "dictionary",
#                     "key_data_name",
#                     "value_data_name",
#
#                     # Optional
#                     "default",
#                 ]:
#                     instance_metadata_items.append(metadata_item)
#                 else:
#                     type_metadata_items.append(metadata_item)
#
#             return _Visitor._SplitMetadata(  # pylint: disable=protected-access
#                 Metadata(metadata.range, type_metadata_items) if type_metadata_items else None,
#                 Metadata(metadata.range, instance_metadata_items) if instance_metadata_items else None,
#             )
#
#     # ----------------------------------------------------------------------
#     # |
#     # |  Private Methods
#     # |
#     # ----------------------------------------------------------------------
#     @staticmethod
#     @contextmanager
#     def _DefaultMethod(
#         element: Element,                   # pylint: disable=unused-argument
#     ) -> Iterator[Optional[VisitResult]]:
#         yield None
#
#     # ----------------------------------------------------------------------
#     @staticmethod
#     def _DefaultDetailMethod(
#         element: Union[Element, List[Element]],         # pylint: disable=unused-argument
#         *,
#         include_disabled: bool,                         # pylint: disable=unused-argument
#     ) -> None:
#         pass
#
#     # ----------------------------------------------------------------------
#     def _InsertPseudoType(
#         self,
#         element: Union[StructureStatement, ItemStatement],
#     ) -> None:
#         # Get the index of this element in the parent's children
#         parent_children = getattr(element.parent, element.parent.CHILDREN_NAME)
#
#         child_index = 0
#         while child_index < len(parent_children):
#             if parent_children[child_index] is element:
#                 break
#
#             child_index += 1
#
#         assert child_index != len(parent_children), (parent_children, element)
#
#         # Disable this element and insert content after it
#         element.Disable()
#         child_index += 1
#
#         # Create an identifier for the new type
#         item_identifier = Identifier(
#             element.range,
#             SimpleElement(element.range, "_PseudoType{}_Element".format(self._pseudo_ctr)),
#             SimpleElement(element.range, Visibility.Private),
#         )
#
#         self._pseudo_ctr += 1
#
#         if isinstance(element, StructureStatement):
#             current_cardinality = element.cardinality
#             current_metadata = element.metadata
#
#             create_new_element_func = lambda metadata: StructureStatement(
#                 element.range,
#                 item_identifier,
#                 element.base,
#                 Cardinality(element.range, None, None),
#                 metadata,
#                 element.children,
#             )
#
#         elif isinstance(element, ItemStatement):
#             current_cardinality = element.type.cardinality
#             current_metadata = element.type.metadata
#
#             # ----------------------------------------------------------------------
#             def CreateNewItemStatement(
#                 metadata: Optional[Metadata],
#             ) -> ItemStatement:
#                 new_type = copy.deepcopy(element.type)
#
#                 object.__setattr__(new_type, "cardinality", Cardinality(element.range, None, None))
#                 object.__setattr__(new_type, "metadata", metadata)
#
#                 return ItemStatement(element.range, item_identifier, new_type)
#
#             # ----------------------------------------------------------------------
#
#             create_new_element_func = CreateNewItemStatement
#
#         else:
#             assert False, element  # pragma: no cover
#
#         metadata = self.__class__._SplitMetadata.Create(current_metadata)  # pylint: disable=protected-access
#
#         parent_children.insert(child_index, create_new_element_func(metadata.type))
#
#         parent_children.insert(
#             child_index + 1,
#             ItemStatement(
#                 element.range,
#                 element.name,
#                 IdentifierType(
#                     element.range,
#                     current_cardinality,
#                     metadata.instance,
#                     [item_identifier, ],
#                     None,
#                 ),
#             ),
#         )
#
