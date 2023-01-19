# ----------------------------------------------------------------------
# |
# |  __main__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-11 13:38:26
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""BugBug (__main__ header)"""

import itertools
import os
import sys
import textwrap
import traceback

from contextlib import contextmanager
from enum import auto, Enum
from pathlib import Path
from typing import Any, Callable, cast, Dict, Generator, Iterator, List, Optional, Tuple, Union

import typer

from typer.core import TyperGroup

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Streams.DoneManager import DoneManager, DoneManagerException
from Common_Foundation import TextwrapEx
from Common_Foundation.Types import overridemethod

from Common_FoundationEx.CompilerImpl.CodeGenerator import CodeGenerator as CodeGeneratorBase, CreateCleanCommandLineFunc, CreateGenerateCommandLineFunc, CreateListCommandLineFunc, InputType, InvokeReason
from Common_FoundationEx.CompilerImpl.Mixins.CodeGeneratorPluginHostMixin import CodeGeneratorPluginHostMixin
from Common_FoundationEx.CompilerImpl.Mixins.InputProcessorMixins.AtomicInputProcessorMixin import AtomicInputProcessorMixin
from Common_FoundationEx.CompilerImpl.Mixins.InvocationQueryMixins.ConditionalInvocationQueryMixin import ConditionalInvocationQueryMixin
from Common_FoundationEx.CompilerImpl.Mixins.OutputProcessorMixins.MultipleOutputProcessorMixin import MultipleOutputProcessorMixin

from Common_FoundationEx import ExecuteTasks
from Common_FoundationEx import TyperEx

from SimpleSchema.Plugin import Plugin

from SimpleSchema.Schema.Elements.Common.Element import Element, SimpleElement
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Statements.ExtensionStatement import ExtensionStatement
from SimpleSchema.Schema.Elements.Statements.ItemStatement import ItemStatement
from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement
from SimpleSchema.Schema.Elements.Statements.StructureStatement import StructureStatement

from SimpleSchema.Schema.Parse import Parse

from SimpleSchema.Schema.Visitors.Visitor import Visitor, VisitResult


# ----------------------------------------------------------------------
class NaturalOrderGrouper(TyperGroup):
    # pylint: disable=missing-class-docstring
    # ----------------------------------------------------------------------
    def list_commands(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.commands.keys()


# ----------------------------------------------------------------------
app                                         = typer.Typer(
    cls=NaturalOrderGrouper,
    help=__doc__,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False,
)


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
class CodeGenerator(
    CodeGeneratorBase,
    AtomicInputProcessorMixin,
    MultipleOutputProcessorMixin,
    CodeGeneratorPluginHostMixin,
):
    """Generates code based on a plugin and SimpleSchema files."""

    DYNAMIC_PLUGINS_ENVIRONMENT_VARIABLE_NAME           = "SIMPLE_SCHEMA_DYNAMIC_PLUGINS"

    # ----------------------------------------------------------------------
    def __init__(
        self,
    ):
        CodeGeneratorBase.__init__(
            self,
            self,
            self,
            "SimpleSchema",
            CodeGenerator.__doc__,
            InputType.Files,
            can_execute_in_parallel=True,
        )

        AtomicInputProcessorMixin.__init__(self)
        MultipleOutputProcessorMixin.__init__(self, self)

        if os.getenv(self.__class__.DYNAMIC_PLUGINS_ENVIRONMENT_VARIABLE_NAME):
            plugin_host_init_args = self.__class__.DYNAMIC_PLUGINS_ENVIRONMENT_VARIABLE_NAME
        else:
            plugin_host_init_args = Path(__file__).parent / "Plugins"

        CodeGeneratorPluginHostMixin.__init__(self, plugin_host_init_args)

    # ----------------------------------------------------------------------
    @overridemethod
    def GetCustomCommandLineArgs(self) -> TyperEx.TypeDefinitionsType:
        default_metadata: Dict[str, Any] = {
            k: v
            for k, v in self._EnumerateOptionalMetadata()
        }

        # Ensure that these bool values are the expected values, as the flag names will need
        # to change if the default values change.
        assert default_metadata["force"] is False

        assert default_metadata["filter_unsupported_extensions"] is False
        assert default_metadata["filter_unsupported_metadata"] is False

        assert default_metadata["preserve_dir_structure"] is True

        return {
            "plugin": (str, typer.Option(default_metadata["plugin"], help="BugBug.")),

            "force": (bool, typer.Option(default_metadata["force"], "--force", help="Force the generation of content, even when no changes are detected.")),

            "filter_unsupported_extensions": (bool, typer.Option(default_metadata["filter_unsupported_extensions"], "--filter-unsupported_extensions", help="BugBug.")),
            "filter_unsupported_metadata": (bool, typer.Option(default_metadata["filter_unsupported_metadata"], "--filter-unsupported-metadata", help="BugBug.")),

            "preserve_dir_structure": (bool, typer.Option(default_metadata["preserve_dir_structure"], "--no-preserve-dir-structure", help="Output all files to the output directory, rather than creating a hierarchy based on the input files encountered.")),
        }

    # ----------------------------------------------------------------------
    @overridemethod
    def IsSupported(
        self,
        filename_or_directory: Path,
    ) -> bool:
        return (
            filename_or_directory.is_file()
            and filename_or_directory.suffix.lower() == ".simpleschema"
        )

    # ----------------------------------------------------------------------
    def LoadPlugin(self, *args, **kwargs) -> Plugin:
        # Make ./Plugin.py easily importable
        sys.path.insert(0, str(Path(__file__).parent))
        with ExitStack(lambda: sys.path.pop(0)):
            return cast(Plugin, super(CodeGenerator, self).LoadPlugin(*args, **kwargs))

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    class _Steps(Enum):
        Parsing                             = 1
        Validating                          = auto()
        Generating                          = auto()

    # ----------------------------------------------------------------------
    _FILENAME_MAP_ATTRIBUTE_NAME            = "_filename_map"

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @overridemethod
    def _EnumerateOptionalMetadata(self) -> Generator[Tuple[str, Any], None, None]:
        yield "plugin", "None"

        yield "filter_unsupported_extensions", False
        yield "filter_unsupported_metadata", False

        yield "preserve_dir_structure", True

        yield from super(CodeGenerator, self)._EnumerateOptionalMetadata()

    # ----------------------------------------------------------------------
    @overridemethod
    def _GetNumStepsImpl(
        self,
        context: Dict[str, Any],
    ) -> int:
        return len(CodeGenerator._Steps) \
            + self.LoadPlugin(context, None).GetNumAdditionalSteps(context)

    # ----------------------------------------------------------------------
    @overridemethod
    def _CreateContext(
        self,
        dm: DoneManager,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        plugin = self.LoadPlugin(metadata, dm)

        metadata[self.__class__._FILENAME_MAP_ATTRIBUTE_NAME] = plugin.GenerateOutputFilenames(
            metadata[AtomicInputProcessorMixin.INPUT_ROOT_ATTRIBUTE_NAME],
            metadata[AtomicInputProcessorMixin.ATTRIBUTE_NAME],
            metadata[ConditionalInvocationQueryMixin.OUTPUT_DIR_ATTRIBUTE_NAME],
            preserve_dir_structure=metadata.pop("preserve_dir_structure"),
        )

        metadata[MultipleOutputProcessorMixin.ATTRIBUTE_NAME] = list(
            itertools.chain(*metadata[self.__class__._FILENAME_MAP_ATTRIBUTE_NAME].values()),
        )

        return super(CodeGenerator, self)._CreateContext(dm, metadata)

    # ----------------------------------------------------------------------
    @overridemethod
    def _InvokeImpl(
        self,
        invoke_reason: InvokeReason,
        dm: DoneManager,
        context: Dict[str, Any],
        on_progress_func: Callable[
            [
                int,                        # Step (0-based)
                str,                        # Status
            ],
            bool,                           # True to continue, False to terminate
        ],
    ) -> Optional[str]:                     # Optional short description that provides input about the result
        # Parse
        on_progress_func(CodeGenerator._Steps.Parsing.value, "Parsing...")

        input_root = context[AtomicInputProcessorMixin.INPUT_ROOT_ATTRIBUTE_NAME]

        # ----------------------------------------------------------------------
        def CreateReadFunc(
            input_filename: Path,
        ) -> Callable[[], str]:
            # ----------------------------------------------------------------------
            def Impl() -> str:
                with input_filename.open() as f:
                    return f.read()

            # ----------------------------------------------------------------------

            return Impl

        # ----------------------------------------------------------------------

        workspace_files: dict[Path, Callable[[], str]] = {
            cast(Path, PathEx.CreateRelativePath(input_root, input_filename)): CreateReadFunc(input_filename)
            for input_filename in context[AtomicInputProcessorMixin.ATTRIBUTE_NAME]
        }

        results = Parse(
            dm,
            {
                input_root: workspace_files,
            },
            single_threaded=False,
            quiet=False,
            raise_if_single_exception=False,
        )

        if dm.result != 0:
            assert all(isinstance(result, Exception) for result in results.values()), results
            _PrintExceptions(dm, cast(dict[Path, Exception], results))

            return None

        roots = cast(Dict[Path, RootStatement], results)

        plugin = self.LoadPlugin(context, dm)

        # Validate
        on_progress_func(CodeGenerator._Steps.Validating.value, "Validating...")

        visitor = _ValidateVisitor(
            plugin,
            filter_unsupported_extensions=context.pop("filter_unsupported_extensions"),
            filter_unsupported_metadata=context.pop("filter_unsupported_metadata"),
        )

        _ExecuteInParallel(
            dm,
            "Validating",
            roots,
            lambda filename, root, on_status_func: cast(None, root.Accept(visitor)),
        )

        if dm.result < 0:
            return None

        # Generate
        on_progress_func(CodeGenerator._Steps.Generating.value, "Generating...")

        # ----------------------------------------------------------------------
        def Generate(
            filename: Path,
            root: RootStatement,
            on_status_func: Callable[[str], None],
        ) -> None:
            key = context[AtomicInputProcessorMixin.INPUT_ROOT_ATTRIBUTE_NAME] / filename
            assert key in context[self.__class__._FILENAME_MAP_ATTRIBUTE_NAME], key

            plugin.Generate(
                context[self.__class__._FILENAME_MAP_ATTRIBUTE_NAME][key],
                root,
                on_status_func,
            )

        # ----------------------------------------------------------------------

        _ExecuteInParallel(
            dm,
            "Generating",
            roots,
            Generate,
        )

        if dm.result < 0:
            return None

        return None


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
_code_generator                             = CodeGenerator()

Generate                                    = CreateGenerateCommandLineFunc(app, _code_generator)
Clean                                       = CreateCleanCommandLineFunc(app, _code_generator)
List                                        = CreateListCommandLineFunc(app, _code_generator)


# ----------------------------------------------------------------------
# |
# |  Private Types
# |
# ----------------------------------------------------------------------
class _ValidateVisitor(Visitor):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        plugin: Plugin,
        *,
        filter_unsupported_extensions: bool,
        filter_unsupported_metadata: bool,
    ):
        self.plugin                         = plugin

        self.filter_unsupported_extensions  = filter_unsupported_extensions
        self.filter_unsupported_metadata    = filter_unsupported_metadata

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
    @contextmanager
    def OnExtensionStatement(self, element: ExtensionStatement) -> Iterator[Optional[VisitResult]]:
        if element.name.id.value not in self.plugin.custom_extension_names:
            if self.filter_unsupported_extensions:
                element.Disable()
                yield VisitResult.SkipAll

            raise SimpleSchemaException(
                "The extension '{}' is not recognized by this plugin.".format(element.name.id.value),
                element.name.id.range,
            )

        with self.plugin.OnExtensionStatement(element) as visit_result:
            if visit_result is None and element.is_disabled:
                visit_result = VisitResult.SkipAll

            yield visit_result

    # ----------------------------------------------------------------------
    @contextmanager
    def OnItemStatement(self, element: ItemStatement) -> Iterator[Optional[VisitResult]]:
        is_root = isinstance(element.parent, RootStatement)

        if is_root and not self.plugin.flags & Plugin.Flag.AllowRootItems:
            raise SimpleSchemaException("Root items are not supported by this plugin.", element.range)

        if not is_root and not self.plugin.flags & Plugin.Flag.AllowNestedItems:
            raise SimpleSchemaException("Nested items are not supported by this plugin.", element.range)

        # BugBug if element.type.metadata is not None:
        # BugBug     for metadata_item in element.type.metadata.items.values():
        # BugBug         assert False, "BugBug"

        with self.plugin.OnItemStatement(element) as visit_result:
            if visit_result is None and element.is_disabled:
                visit_result = VisitResult.SkipAll

            yield visit_result

    # ----------------------------------------------------------------------
    @contextmanager
    def OnStructureStatement(self, element: StructureStatement) -> Iterator[Optional[VisitResult]]:
        is_root = isinstance(element.parent, RootStatement)

        if is_root and not self.plugin.flags & Plugin.Flag.AllowRootStructures:
            raise SimpleSchemaException("Root structures are not supported by this plugin.", element.range)

        if not is_root and not self.plugin.flags & Plugin.Flag.AllowNestedStructures:
            raise SimpleSchemaException("Nested structures are not supported by this plugin.", element.range)

        resolved_metadata: dict[str, SimpleElement] = {}

        if element.metadata is not None:
            for metadata_item in list(element.metadata.items.values()):
                prev_resolved_metadata = resolved_metadata.get(metadata_item.name.id.value, None)
                if prev_resolved_metadata is not None:
                    raise SimpleSchemaException(
                        "The metadata item '{}' has already been specified for this structure ({}).".format(
                            metadata_item.name.id.value,
                            prev_resolved_metadata.range.ToString(include_filename=False),
                        ),
                        metadata_item.name.id.range,
                    )

                # Resolve the metadata item using the attribute it corresponds to
                attribute = self.plugin.custom_metadata_attributes.get(metadata_item.name.id.value, None)
                if attribute is None:
                    if self.filter_unsupported_metadata:
                        metadata_item.Disable()
                        continue

                    raise SimpleSchemaException(
                        "The metadata item '{}' is not recognized by this plugin.".format(metadata_item.name.id.value),
                        metadata_item.name.range,
                    )

                attribute.Validate(element)

                attribute_value = attribute.type.ParseExpression(metadata_item.value)

                resolved_metadata[metadata_item.name.id.value] = SimpleElement(
                    metadata_item.value.range,
                    attribute_value,
                )

        assert not hasattr(element, "resolved_metadata")
        object.__setattr__(element, "resolved_metadata", resolved_metadata)

        with self.plugin.OnStructureStatement(element) as visit_result:
            if visit_result is None and element.is_disabled:
                visit_result = VisitResult.SkipAll

            yield visit_result

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
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
        elif callable(element_or_elements):
            # We are looking at a weakref, don't follow it
            return VisitResult.Continue
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
    @contextmanager
    def _DefaultMethod(self, *args, **kwargs) -> Iterator[Optional[VisitResult]]:
        yield


# ----------------------------------------------------------------------
# |
# |  Private Functions
# |
# ----------------------------------------------------------------------
def _ExecuteInParallel(
    dm: DoneManager,
    heading: str,
    roots: dict[Path, RootStatement],
    func: Callable[[Path, RootStatement, Callable[[str], None]], None],
) -> None:
    # ----------------------------------------------------------------------
    def Execute(
        context: Tuple[Path, RootStatement],
        on_simple_status_func: Callable[[str], None],  # pylint: disable=unused-argument
    ) -> Tuple[Optional[int], ExecuteTasks.TransformStep2FuncType[Optional[Exception]]]:
        filename, root = context
        del context

        # ----------------------------------------------------------------------
        def Impl(
            status: ExecuteTasks.Status,
        ) -> Tuple[Optional[Exception], Optional[str]]:
            func(filename, root, lambda value: cast(None, status.OnProgress(None, value)))
            return None, None

        # ----------------------------------------------------------------------

        return None, Impl

    # ----------------------------------------------------------------------

    results: list[Optional[Exception]] = ExecuteTasks.Transform(
        dm,
        heading,
        [
            ExecuteTasks.TaskData(str(filename), (filename, root))
            for filename, root in roots.items()
        ],
        # The Optional return type confuses linters
        Execute,  # type: ignore
        return_exceptions=True,
        max_num_threads=1, # BugBug
    )

    exceptions: dict[Path, Exception] = {}

    for filename, result in zip(roots.keys(), results):
        if result is None:
            continue

        exceptions[filename] = result

    if exceptions:
        _PrintExceptions(dm, exceptions)


# ----------------------------------------------------------------------
def _PrintExceptions(
    dm: DoneManager,
    exceptions: dict[Path, Exception],
) -> None:
    if dm.is_debug:
        error_string_func = lambda ex: "".join(traceback.format_exception(ex))
    else:
        error_string_func = str

    for filename, exception in exceptions.items():
        dm.WriteError(
            textwrap.dedent(
                """\
                {} ->

                    {}

                """,
            ).format(
                filename,
                TextwrapEx.Indent(error_string_func(exception).rstrip(), 4, skip_first_line=True),
            ),
        )

    dm.WriteLine("")



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app()
