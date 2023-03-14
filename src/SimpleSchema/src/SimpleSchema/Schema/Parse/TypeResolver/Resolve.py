# ----------------------------------------------------------------------
# |
# |  Resolve.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-23 12:59:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, cast, Iterator, Optional, Type as TypeOf, TypeVar, Union

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation.Streams.DoneManager import DoneManager
from Common_Foundation.Types import overridemethod

from .Impl.Namespace import Namespace
from .Impl.TypeFactories import ReferenceTypeFactory, StructureTypeFactory

from ..ANTLR.Elements.Common.ParseIdentifier import ParseIdentifier
from ..ANTLR.Elements.Statements.ParseIncludeStatement import ParseIncludeStatement
from ..ANTLR.Elements.Statements.ParseItemStatement import ParseItemStatement
from ..ANTLR.Elements.Statements.ParseStructureStatement import ParseStructureStatement
from ..ANTLR.Elements.Types.ParseIdentifierType import ParseIdentifierType

from ..ParseState.ParseState import ParseState
from ..Visitor import Visitor, VisitResult

from ...Elements.Common.Cardinality import Cardinality
from ...Elements.Common.Visibility import Visibility

from ...Elements.Statements.RootStatement import RootStatement

from ...Elements.Types.FundamentalType import FundamentalType
from ...Elements.Types.FundamentalTypes import AllFundamentalTypes

from ....Common import Errors
from ....Common.ExecuteInParallel import ExecuteInParallel as ExecuteInParallelImpl


# ----------------------------------------------------------------------
def Resolve(
    dm: DoneManager,
    parse_state: ParseState,  # pylint: disable=unused-argument
    roots: dict[Path, RootStatement],
    *,
    single_threaded: bool=False,
    quiet: bool=False,
    raise_if_single_exception: bool=True,
) -> Optional[dict[Path, Exception]]:
    max_num_threads = 1 if single_threaded else None

    # Create namespaces
    with dm.VerboseNested("Creating namespaces...") as verbose_dm:
        # ----------------------------------------------------------------------
        def CreateNamespace(
            root: RootStatement,
        ) -> Namespace:
            root_namespace = Namespace(
                None,
                Visibility.Public,
                "root",
                root,
                None,
            )

            root.Accept(_CreateNamespacesVisitor(root, root_namespace))

            return root_namespace

        # ----------------------------------------------------------------------

        namespaces = _ExecuteInParallel(
            verbose_dm,
            roots,
            CreateNamespace,
            quiet=quiet,
            max_num_threads=max_num_threads,
            raise_if_single_exception=raise_if_single_exception,
        )

        if verbose_dm.result != 0:
            assert all(isinstance(value, Exception) for value in namespaces.values()), namespaces
            return cast(dict[Path, Exception], namespaces)

        namespaces = cast(dict[Path, Namespace], namespaces)

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
            assert all(isinstance(value, Exception) for value in results.values()), namespaces
            return cast(dict[Path, Exception], results)

    # Ensure unique type names
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
            assert all(isinstance(value, Exception) for value in results.values()), namespaces
            return cast(dict[Path, Exception], results)

    # Resolve types
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
            assert all(isinstance(value, Exception) for value in results.values()), namespaces
            return cast(dict[Path, Exception], results)

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
            assert all(isinstance(value, Exception) for value in results.values()), namespaces
            return cast(dict[Path, Exception], results)

    return None


# ----------------------------------------------------------------------
# |
# |  Private Types
# |
# ----------------------------------------------------------------------
class _CreateNamespacesVisitor(Visitor):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        root: RootStatement,
        root_namespace: Namespace,
    ):
        super(_CreateNamespacesVisitor, self).__init__()

        self._root                          = root

        self._namespace_stack: list[Namespace]          = [root_namespace, ]

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnParseIncludeStatement(
        self,
        element: ParseIncludeStatement,
    ) -> Iterator[Optional[VisitResult]]:
        self._namespace_stack[-1].AddIncludeStatement(element)

        yield

        element.Disable()

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnParseItemStatement(
        self,
        element: ParseItemStatement,
    ) -> Iterator[Optional[VisitResult]]:
        yield

        if element.name.is_type:
            self._namespace_stack[-1].AddNestedItem(
                element.name.ToSimpleElement(),
                ReferenceTypeFactory(element, self._namespace_stack[-1]),
            )

        elif element.name.is_expression:
            self._namespace_stack[-1].AddItemStatement(element)

        else:
            assert False, element.name  # pragma: no cover

    # ----------------------------------------------------------------------
    @overridemethod
    @contextmanager
    def OnParseStructureStatement(
        self,
        element: ParseStructureStatement,
    ) -> Iterator[Optional[VisitResult]]:
        if element.name.is_expression:
            if not element.children:
                raise Errors.ResolveStructureStatementEmptyPseudoElement.Create(element.range)

            # Create a pseudo element for this Typedef
            unique_type_name = "_PseudoType-Ln{}".format(element.range.begin.line)

            new_structure = ParseStructureStatement(
                element.range,
                ParseIdentifier(element.range, unique_type_name),
                element.bases,
                element.cardinality,
                element.unresolved_metadata,
                element.children,
            )

            new_reference = ParseItemStatement(
                element.range,
                element.name,
                ParseIdentifierType(
                    element.range,
                    Cardinality(element.range, None, None),
                    None,
                    [
                        ParseIdentifier(element.range, unique_type_name),
                    ],
                    None,
                    None,
                ),
            )

            # Add the new elements and disable the current one
            parents_children, sibling_index = self._namespace_stack[-1].GetSiblingInfo(element)

            parents_children.insert(sibling_index + 1, new_structure)
            parents_children.insert(sibling_index + 2, new_reference)

            element.Disable()

            yield VisitResult.SkipAll
            return

        assert element.name.is_type

        namespace = Namespace(
            self._namespace_stack[-1],
            element.name.visibility.value,
            element.name.value,
            element,
            StructureTypeFactory(element, self._namespace_stack[-1]),
        )

        self._namespace_stack[-1].AddNestedItem(
            element.name.ToSimpleElement(),
            namespace,
        )

        self._namespace_stack.append(namespace)
        with ExitStack(self._namespace_stack.pop):
            yield


# ----------------------------------------------------------------------
# |
# |  Private Functions
# |
# ----------------------------------------------------------------------
_ExecuteInParallelInputT                    = TypeVar("_ExecuteInParallelInputT")
_ExecuteInParallelOutputT                   = TypeVar("_ExecuteInParallelOutputT")

def _ExecuteInParallel(
    dm: DoneManager,
    items: dict[Path, _ExecuteInParallelInputT],
    func: Callable[[_ExecuteInParallelInputT], _ExecuteInParallelOutputT],
    *,
    quiet: bool,
    max_num_threads: Optional[int],
    raise_if_single_exception: bool,
) -> Union[
    dict[Path, Exception],
    dict[Path, _ExecuteInParallelOutputT],
]:
    return ExecuteInParallelImpl(
        dm,
        "Processing",
        items,
        lambda context, status: func(context),
        quiet=quiet,
        max_num_threads=max_num_threads,
        raise_if_single_exception=raise_if_single_exception,
    )


# ----------------------------------------------------------------------
def _LoadFundamentalTypes() -> dict[str, TypeOf[FundamentalType]]:
    types: dict[str, TypeOf[FundamentalType]] = {}

    for class_name in dir(AllFundamentalTypes):
        if not class_name.endswith("Type"):
            continue

        fundamental_type_class = getattr(AllFundamentalTypes, class_name)

        assert fundamental_type_class.NAME not in types, fundamental_type_class.NAME
        types[fundamental_type_class.NAME] = fundamental_type_class

    return types
