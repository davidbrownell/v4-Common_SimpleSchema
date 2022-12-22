# ----------------------------------------------------------------------
# |
# |  ToPythonDictVisitor.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-16 11:39:42
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ToPythonDictVisitor object"""

import re

from typing import Any, List, Dict, Union

from Common_Foundation.Types import overridemethod

from SimpleSchema.Schema.Visitors.Visitor import *  # pylint: disable=wildcard-import,unused-wildcard-import


# ----------------------------------------------------------------------
class ToPythonDictVisitor(Visitor):
    """Converts items to a python dict"""

    # ----------------------------------------------------------------------
    def __init__(self):
        self._stack: List[Dict[str, Any]]   = []

        self._details_regex                 = re.compile(r"^On(?P<object_name>.+?)__(?P<member_name>.+)$")

    # ----------------------------------------------------------------------
    @property
    def root(self) -> List[Dict[str, Any]]:
        assert len(self._stack) == 1, self._stack
        return self._stack

    # ----------------------------------------------------------------------
    def __getattr__(
        self,
        name: str,
    ):
        match = self._details_regex.match(name)
        if match:
            return lambda *args, **kwargs: self._DefaultDetailMethod(match.group("member_name"), *args, **kwargs)

        raise AttributeError(name)

    # ----------------------------------------------------------------------
    # |  Generic Methods
    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnElement(
        self,
        element: Element,  # pylint: disable=unused-argument
    ) -> Iterator[Optional[VisitResult]]:
        self._stack.append(
            {
                "__type__": element.__class__.__name__,
                "range": element.range.ToString(),
            },
        )

        yield

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnElementChildren(
        self,
        element: Element,  # pylint: disable=unused-argument
    ) -> Iterator[Optional[VisitResult]]:
        prev_num_items = len(self._stack)

        yield

        children = self._stack[prev_num_items:]
        self._stack = self._stack[:prev_num_items]

        d = self._stack[-1]

        d[element.CHILDREN_NAME] = children

    # ----------------------------------------------------------------------
    @contextmanager
    def OnSimpleElement(
        self,
        element: SimpleElement,
    ) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        value = element.value

        if value is not None and not isinstance(value, (str, int, float, bool)):
            value = str(value)

        d["value"] = value

        yield

    # ----------------------------------------------------------------------
    # |  Common Methods
    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnCardinality(self, element: Cardinality) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnIdentifier(self, element: Identifier) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnMetadata(self, element: Metadata) -> Iterator[Optional[VisitResult]]:
        # No custom processing required
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnMetadataItem(self, element: MetadataItem) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    # |  Expressions
    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnBooleanExpression(self, element: BooleanExpression) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        d.update(
            value=element.value,
        )

        yield

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnIdentifierExpression(self, element: IdentifierExpression) -> Iterator[Optional[VisitResult]]:
        with self.OnIdentifier(element) as result:
            yield result

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnIntegerExpression(self, element: IntegerExpression) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        d.update(
            value=element.value,
        )

        yield

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnListExpression(self, element: ListExpression) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnNumberExpression(self, element: NumberExpression) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        d.update(
            value=element.value,
        )

        yield

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnStringExpression(self, element: StringExpression) -> Iterator[Optional[VisitResult]]:
        d = self._stack[-1]

        d.update(
            value=element.value,
        )

        yield

    # ----------------------------------------------------------------------
    # |  Statements
    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnIncludeStatement(self, element: IncludeStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnIncludeStatementItem(self, element: IncludeStatementItem) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnExtensionStatement(self, element: ExtensionStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnExtensionStatementKeywordArg(self, element: ExtensionStatementKeywordArg) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnItemStatement(self, element: ItemStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnRootStatement(self, element: RootStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    # |  Types
    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnIdentifierType(self, element: IdentifierType) -> Iterator[Optional[VisitResult]]:
        if element.element_reference:
            self._stack[-1]["element_reference"] = element.element_reference.ToString()

        yield

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnTupleType(self, element: TupleType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnVariantType(self, element: VariantType) -> Iterator[Optional[VisitResult]]:
        yield

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _DefaultDetailMethod(
        self,
        member_name: str,
        element_or_elements: Union[Element, List[Element]],
        *,
        include_disabled: bool,
    ):
        prev_num_elements = len(self._stack)

        if isinstance(element_or_elements, list):
            is_list = True

            for element in element_or_elements:
                if not element.is_disabled or include_disabled:
                    element.Accept(
                        self,
                        include_disabled=include_disabled,
                    )
        else:
            is_list = False

            if not element_or_elements.is_disabled or include_disabled:
                element_or_elements.Accept(
                    self,
                    include_disabled=include_disabled,
                )

        children = self._stack[prev_num_elements:]
        self._stack = self._stack[:prev_num_elements]

        if not is_list:
            assert 0 <= len(children) <= 1
            if children:
                children = children[0]
            else:
                children = None

        d = self._stack[-1]

        d[member_name] = children
