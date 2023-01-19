# ----------------------------------------------------------------------
# |
# |  TypeResolver.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-10 16:46:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that resolves types"""

from contextlib import contextmanager
from pathlib import Path
from typing import Callable, cast, Dict, Iterator, List, Optional, Tuple, Type as TypeOf, TypeVar, Union

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation.Streams.DoneManager import DoneManager
from Common_Foundation.Types import overridemethod

from Common_FoundationEx import ExecuteTasks

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Element import Element, SimpleElement
from SimpleSchema.Schema.Elements.Common.Identifier import Identifier, Visibility

from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement

from SimpleSchema.Schema.Elements.Types.FundamentalType import FundamentalType
from SimpleSchema.Schema.Elements.Types import FundamentalTypes

from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseIncludeStatement import ParseIncludeStatement
from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseItemStatement import ParseItemStatement
from SimpleSchema.Schema.Parse.ANTLR.Elements.Statements.ParseStructureStatement import ParseStructureStatement

from SimpleSchema.Schema.Parse.ANTLR.Elements.Types.ParseIdentifierType import ParseIdentifierType

from SimpleSchema.Schema.Parse.TypeResolver.ElementFactories import AliasTypeFactory, StructureStatementFactory
from SimpleSchema.Schema.Parse.TypeResolver.Namespaces import Namespace, StructureNamespace

from SimpleSchema.Schema.Visitors.Visitor import Visitor, VisitResult


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def Resolve(
    dm: DoneManager,
    roots: Dict[Path, RootStatement],
    *,
    single_threaded: bool=False,
    quiet: bool=False,
    raise_if_single_exception: bool=False,
) -> Optional[Dict[Path, Exception]]:
    max_num_threads = 1 if single_threaded else None

    # ----------------------------------------------------------------------
    def CreateNamespace(
        root: RootStatement,
    ) -> Namespace:
        root_namespace = Namespace(None, "root", Visibility.Public)

        root.Accept(_CreateNamespacesVisitor(root_namespace))

        return root_namespace

    # ----------------------------------------------------------------------

    # Create namespaces
    with dm.VerboseNested("Creating namespaces...") as verbose_dm:
        namespaces = _ExecuteInParallel(
            verbose_dm,
            roots,
            CreateNamespace,
            quiet=quiet,
            max_num_threads=max_num_threads,
            raise_if_single_exception=raise_if_single_exception,
        )

        if verbose_dm.result != 0:
            assert all(isinstance(value, Exception) for value in namespaces.values())
            return cast(Dict[Path, Exception], namespaces)

    namespaces = cast(Dict[Path, Namespace], namespaces)

    # Resolve Includes
    with dm.VerboseNested("Resolving includes...") as verbose_dm:
        results = _ExecuteInParallel(
            verbose_dm,
            namespaces,
            lambda root_namespace: root_namespace.ResolveIncludes(namespaces),
            quiet=quiet,
            max_num_threads=max_num_threads,
            raise_if_single_exception=raise_if_single_exception,
        )

        if verbose_dm.result != 0:
            assert all(isinstance(value, Exception) for value in results.values())
            return cast(Dict[Path, Exception], results)

    # Ensure unique types
    with dm.VerboseNested("Validating type names...") as verbose_dm:
        results = _ExecuteInParallel(
            verbose_dm,
            namespaces,
            lambda root_namespace: root_namespace.ResolveTypeNames(),
            quiet=quiet,
            max_num_threads=max_num_threads,
            raise_if_single_exception=raise_if_single_exception,
        )

        if verbose_dm.result != 0:
            assert all(isinstance(value, Exception) for value in results.values())
            return cast(Dict[Path, Exception], results)

    # Resolve Types
    with dm.VerboseNested("Resolving types...") as verbose_dm:
        fundamental_types = _LoadFundamentalTypes()

        results = _ExecuteInParallel(
            verbose_dm,
            namespaces,
            lambda root_namespace: root_namespace.ResolveTypes(fundamental_types),
            quiet=quiet,
            max_num_threads=max_num_threads,
            raise_if_single_exception=raise_if_single_exception,
        )

        if verbose_dm.result != 0:
            assert all(isinstance(value, Exception) for value in results.values())
            return cast(Dict[Path, Exception], results)

    # Finalize types
    with dm.VerboseNested("Finalizing types...") as verbose_dm:
        results = _ExecuteInParallel(
            verbose_dm,
            namespaces,
            lambda root_namespace: root_namespace.Finalize(),
            quiet=quiet,
            max_num_threads=max_num_threads,
            raise_if_single_exception=raise_if_single_exception,
        )

        if verbose_dm.result != 0:
            assert all(isinstance(value, Exception) for value in results.values())
            return cast(Dict[Path, Exception], results)

    return None


# ----------------------------------------------------------------------
class _CreateNamespacesVisitor(Visitor):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        root_namespace: Namespace,
    ):
        self._element_stack: List[Element]              = []
        self._namespace_stack: List[Namespace]          = [root_namespace, ]

        self._pseudo_type_ctr: int                      = 0

    # ----------------------------------------------------------------------
    def __getattr__(
        self,
        name: str,
    ):
        if self.DETAILS_REGEX.match(name):
            return self._DefaultDetailsMethod

        if self.METHOD_REGEX.match(name):
            return self._DefaultMethod

        raise AttributeError(name)

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnElement(
        self,
        element: Element,
    ) -> Iterator[Optional[VisitResult]]:
        if self._element_stack:
            element.SetParent(self._element_stack[-1])

        self._element_stack.append(element)
        with ExitStack(self._element_stack.pop):
            yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnParseIncludeStatement(
        self,
        element: ParseIncludeStatement,
    ) -> Iterator[Optional[VisitResult]]:
        self._namespace_stack[-1].AddIncludeStatement(element)

        yield

        element.Disable()

    # ----------------------------------------------------------------------
    @contextmanager
    def OnParseItemStatement(
        self,
        element: ParseItemStatement,
    ) -> Iterator[Optional[VisitResult]]:
        yield

        if element.name.is_type:
            self._namespace_stack[-1].AddNestedItem(
                element.name,
                AliasTypeFactory(element, self._namespace_stack[-1]),
            )
        elif element.name.is_expression:
            self._namespace_stack[-1].AddItemStatement(element)
        else:
            assert False, element.name  # pragma: no cover

    # ----------------------------------------------------------------------
    @contextmanager
    def OnParseStructureStatement(
        self,
        element: ParseStructureStatement,
    ) -> Iterator[Optional[VisitResult]]:
        if element.name.is_expression:
            # Create a pseudo element for this reference
            unique_type_name = "_PseudoType{}".format(self._pseudo_type_ctr)
            self._pseudo_type_ctr += 1

            new_structure = ParseStructureStatement(
                element.range,
                Identifier(
                    element.range,
                    SimpleElement(element.range, unique_type_name),
                    SimpleElement(element.range, Visibility.Private),
                ),
                element.base,
                Cardinality(element.range, None, None, None),
                element.metadata,
                element.children,
            )

            new_reference = ParseItemStatement(
                element.range,
                element.name,
                ParseIdentifierType(
                    element.range,
                    element.cardinality,
                    None,
                    [
                        Identifier(
                            element.range,
                            SimpleElement(element.range, unique_type_name),
                            SimpleElement(element.range, Visibility.Private),
                        ),
                    ],
                    None,
                    None,
                ),
            )

            # Add the new elements and disable the current one
            parents_children, sibling_index = Namespace.GetSiblingInfo(element)

            parents_children.insert(sibling_index + 1, new_structure)
            parents_children.insert(sibling_index + 2, new_reference)

            element.Disable()

            yield VisitResult.SkipAll
            return

        assert element.name.is_type

        structure_namespace = StructureNamespace(
            StructureStatementFactory(element, self._namespace_stack[-1]),
            self._namespace_stack[-1],
            element.name.id.value,
            element.name.visibility.value,
        )

        self._namespace_stack[-1].AddNestedItem(element.name, structure_namespace)

        self._namespace_stack.append(structure_namespace)
        with ExitStack(self._namespace_stack.pop):
            yield

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @contextmanager
    def _DefaultMethod(self, *args, **kwargs) -> Iterator[Optional[VisitResult]]:  # pylint: disable=unused-arguments
        yield

    # ----------------------------------------------------------------------
    def _DefaultDetailsMethod(
        self,
        element_or_elements: Element.GenerateAcceptDetailsGeneratorItemsType,
        *,
        include_disabled: bool,
    ) -> VisitResult:
        if isinstance(element_or_elements, Element):
            elements = [element_or_elements, ]
        elif isinstance(element_or_elements, list):
            elements = element_or_elements
        else:
            assert False, element_or_elements  # pragma: no cover

        del element_or_elements

        for element in elements:
            assert isinstance(element, Element), element

            if element.is_disabled and not include_disabled:
                continue

            result = element.Accept(self, include_disabled=include_disabled)
            if result == VisitResult.Terminate:
                return result

        return VisitResult.Continue


# ----------------------------------------------------------------------
# |
# |  Private Functions
# |
# ----------------------------------------------------------------------
_ExecuteInParallelInputT                    = TypeVar("_ExecuteInParallelInputT")
_ExecuteInParallelOutputT                   = TypeVar("_ExecuteInParallelOutputT")

def _ExecuteInParallel(
    dm: DoneManager,
    items: Dict[Path, _ExecuteInParallelInputT],
    func: Callable[[_ExecuteInParallelInputT], _ExecuteInParallelOutputT],
    *,
    quiet: bool,
    max_num_threads: Optional[int],
    raise_if_single_exception: bool,
) -> Union[
    Dict[Path, Exception],
    Dict[Path, _ExecuteInParallelOutputT],
]:
    # ----------------------------------------------------------------------
    def Execute(
        context: _ExecuteInParallelInputT,
        on_simple_status_func: Callable[[str], None],  # pylint: disable=unused-argument
    ) -> Tuple[
        Optional[int],
        ExecuteTasks.TransformStep2FuncType[Union[Exception, _ExecuteInParallelOutputT]],
    ]:
        # ----------------------------------------------------------------------
        def Impl(
            status: ExecuteTasks.Status,  # pylint: disable=unused-argument
        ) -> Tuple[Union[Exception, _ExecuteInParallelOutputT], Optional[str]]:
            return func(context), None

        # ----------------------------------------------------------------------

        return None, Impl

    # ----------------------------------------------------------------------

    exceptions: Dict[Path, Exception] = {}
    results: Dict[Path, _ExecuteInParallelOutputT] = {}

    for filename, result in zip(
        items.keys(),
        ExecuteTasks.Transform(
            dm,
            "Processing",
            [
                ExecuteTasks.TaskData(str(filename), context)
                for filename, context in items.items()
            ],
            Execute,
            quiet=quiet,
            max_num_threads=max_num_threads,
            return_exceptions=True,
        ),
    ):
        if isinstance(result, Exception):
            exceptions[filename] = result
            dm.result = -1
        elif not exceptions:
            results[filename] = cast(_ExecuteInParallelOutputT, result)

    if raise_if_single_exception and exceptions and len(exceptions) == 1:
        raise next(iter(exceptions.values()))

    return exceptions or results


# ----------------------------------------------------------------------
def _LoadFundamentalTypes() -> Dict[str, TypeOf[FundamentalType]]:
    types: Dict[str, TypeOf[FundamentalType]] = {}

    for name in dir(FundamentalTypes):
        if not name.endswith("Type"):
            continue

        fundamental_type_class = getattr(FundamentalTypes, name)

        assert fundamental_type_class.NAME not in types
        types[fundamental_type_class.NAME] = fundamental_type_class

    return types
