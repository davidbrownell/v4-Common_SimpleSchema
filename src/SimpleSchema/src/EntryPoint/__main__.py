# ----------------------------------------------------------------------
# |
# |  __main__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-30 10:00:16
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Generates code based on a plugin and SimpleSchema files."""

import itertools
import os
import sys
import textwrap
import traceback

from enum import auto, Enum
from pathlib import Path
from typing import Any, Callable, cast, Generator, Optional, Tuple

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Streams.DoneManager import DoneManager
from Common_Foundation import TextwrapEx
from Common_Foundation.Types import DoesNotExist, overridemethod

from Common_FoundationEx.CompilerImpl.CodeGenerator import CodeGenerator as CodeGeneratorBase, CreateCleanCommandLineFunc, CreateGenerateCommandLineFunc, CreateListCommandLineFunc, InputType, InvokeReason
from Common_FoundationEx.CompilerImpl.Mixins.CodeGeneratorPluginHostMixin import CodeGeneratorPluginHostMixin
from Common_FoundationEx.CompilerImpl.Mixins.InputProcessorMixins.AtomicInputProcessorMixin import AtomicInputProcessorMixin
from Common_FoundationEx.CompilerImpl.Mixins.InvocationQueryMixins.ConditionalInvocationQueryMixin import ConditionalInvocationQueryMixin
from Common_FoundationEx.CompilerImpl.Mixins.OutputProcessorMixins.MultipleOutputProcessorMixin import MultipleOutputProcessorMixin

from Common_FoundationEx import ExecuteTasks
from Common_FoundationEx import TyperEx

# typer must be imported after the imports above
import typer

from typer.core import TyperGroup


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    # This configuration (in terms of the items listed below) is the only way that I could get
    # this to work both locally and when frozen as an executable, here and with plugins.
    #
    # Modify at your own risk.
    #
    #   Factors that contributed to this configuration:
    #
    #       - Directory name (which is why there is the funky 'src/SimpleSchema/src/SimpleSchema' layout
    #       - This file as 'EntryPoint/__main__.py' rather than '../EntryPoint.py'
    #       - Build.py/setup.py located outside of 'src'

    from SimpleSchema.Common.ExecuteInParallel import ExecuteInParallel as ExecuteInParallelImpl    # pylint: disable=import-error

    from SimpleSchema.Plugin import Plugin                                                          # pylint: disable=import-error

    from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement                 # pylint: disable=import-error

    from SimpleSchema.Schema.Parse.ANTLR.Parse import Parse                                         # pylint: disable=import-error
    from SimpleSchema.Schema.Parse.Normalize.Normalize import Normalize, Flag as NormalizeFlag      # pylint: disable=import-error
    from SimpleSchema.Schema.Parse.TypeResolver.Resolve import Resolve                              # pylint: disable=import-error


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

    # ----------------------------------------------------------------------
    DYNAMIC_PLUGINS_ENVIRONMENT_VARIABLE_NAME           = "SIMPLE_SCHEMA_DYNAMIC_PLUGINS"

    # ----------------------------------------------------------------------
    def __init__(self):
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
        elif getattr(sys, "frozen", False):
            # Running from source
            plugin_host_init_args = Path(sys.executable).parent / "Plugins"
        else:
            # Frozen
            plugin_host_init_args = Path(__file__).parent.parent / "Plugins"

        CodeGeneratorPluginHostMixin.__init__(self, plugin_host_init_args)

    # ----------------------------------------------------------------------
    @overridemethod
    def GetCustomCommandLineArgs(self) -> TyperEx.TypeDefinitionsType:
        default_metadata: dict[str, Any] = {
            k: v
            for k, v in self._EnumerateOptionalMetadata()
        }

        # Ensure that these bool values are the expected values, as the flag names will need
        # to change if the default values change.
        assert default_metadata["force"] is False

        assert default_metadata["filter_unsupported_extensions"] is False
        assert default_metadata["filter_unsupported_metadata"] is False
        assert default_metadata["filter_unsupported_root_elements"] is False
        assert default_metadata["filter_unsupported_nested_elements"] is False

        assert default_metadata["preserve_dir_structure"] is True

        return {
            "plugin": (str, typer.Option(default_metadata["plugin"], help="Name of a plugin to use for generation (or a fullpath to a python file containing a Plugin class).")),

            "force": (bool, typer.Option(default_metadata["force"], "--force", help="Force the generation of content, even when no changes are detected.")),

            "filter_unsupported_extensions": (bool, typer.Option(default_metadata["filter_unsupported_extensions"], "--filter-unsupported-extensions", help="Do not issue an error (and instead ignore it) when an extension is found that is not supported by the current plugin.")),
            "filter_unsupported_metadata": (bool, typer.Option(default_metadata["filter_unsupported_metadata"], "--filter-unsupported-metadata", help="Do not issue an error (and instead ignore it) when metadata is found that is not supported by the current plugin.")),
            "filter_unsupported_root_elements": (bool, typer.Option(default_metadata["filter_unsupported_root_elements"], "--filter-unsupported-root-elements", help="Do not issue an error (and instead ignore it) when a root element is encountered by a plugin that does not support root elements of that type.")),
            "filter_unsupported_nested_elements": (bool, typer.Option(default_metadata["filter_unsupported_nested_elements"], "--filter-unsupported-nested-elements", help="Do not issue an error (and instead ignore it) when a nested element is encountered by a plugin that does not support nested elements of that type.")),

            "preserve_dir_structure": (bool, typer.Option(default_metadata["preserve_dir_structure"], "--no-preserve-dir-structure", help="Output all files to the output directory, rather than creating a hierarchy based on the input files encountered.")),

            ConditionalInvocationQueryMixin.OUTPUT_DATA_FILENAME_PREFIX_ATTRIBUTE_NAME: (str, typer.Option(default_metadata[ConditionalInvocationQueryMixin.OUTPUT_DATA_FILENAME_PREFIX_ATTRIBUTE_NAME], "--output-data-filename-prefix", help="Prefix to apply to information used to determine if recompilation is necessary; this can be useful when multiple plugins generate output content into the same directory.")),
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
    def GetPlugin(
        self,
        metadata_or_context: dict[str, Any],
    ) -> Plugin:
        return cast(Plugin, super(CodeGenerator, self).GetPlugin(metadata_or_context))

    # ----------------------------------------------------------------------
    @overridemethod
    def ValidateMetadata(
        self,
        dm: DoneManager,
        metadata: dict[str, Any],
    ) -> None:
        plugin = self.GetPlugin(metadata)

        plugin_type_definitions = TyperEx.ResolveTypeDefinitions(
            plugin.GetCommandLineArgs(),
            assume_optional=True,
        )

        if metadata.pop("plugin_help", False):
            # ----------------------------------------------------------------------
            def GetParamName(
                name: str,
                info: TyperEx.typer_models.OptionInfo,
            ) -> str:
                if info.param_decls:
                    return info.param_decls[0]

                return "--{}".format(name)

            # ----------------------------------------------------------------------

            dm.WriteLine(
                textwrap.dedent(
                    """\
                    Arguments for the plugin '{}':

                        {}

                    """,
                ).format(
                    plugin.name,
                    TextwrapEx.Indent(
                        TextwrapEx.CreateTable(
                            [
                                "Arg Name",
                                "Type",
                                "Default Value",
                                "Description",
                            ],
                            [
                                [
                                    GetParamName(plugin_type_name, plugin_type_def.option_info),
                                    plugin_type_def.python_type.__name__,
                                    str(plugin_type_def.option_info.default),
                                    plugin_type_def.option_info.help or "",
                                ]
                                for plugin_type_name, plugin_type_def in plugin_type_definitions.items()
                            ],
                        ),
                        4,
                        skip_first_line=True,
                    ),
                ),
            )

            dm.result = 1
            return

        for k, v in TyperEx.ProcessArguments(
            plugin_type_definitions,
            metadata.pop("plugin_args", {}).items(),
            assume_optional=True,
        ).items():
            assert k not in metadata, (k, metadata[k])
            metadata[k] = v

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
        yield "filter_unsupported_root_elements", False
        yield "filter_unsupported_nested_elements", False

        yield "preserve_dir_structure", True

        yield from super(CodeGenerator, self)._EnumerateOptionalMetadata()

    # ----------------------------------------------------------------------
    @overridemethod
    def _GetNumStepsImpl(
        self,
        context: dict[str, Any],
    ) -> int:
        return len(CodeGenerator._Steps) \
            + self.GetPlugin(context).GetNumAdditionalSteps(context)

    # ----------------------------------------------------------------------
    @overridemethod
    def _CreateContext(
        self,
        dm: DoneManager,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        plugin = self.GetPlugin(metadata)

        metadata[self.__class__._FILENAME_MAP_ATTRIBUTE_NAME] = plugin.GenerateOutputFilenames(  # pylint: disable=protected-access
            metadata[AtomicInputProcessorMixin.INPUT_ROOT_ATTRIBUTE_NAME],
            metadata[AtomicInputProcessorMixin.ATTRIBUTE_NAME],
            metadata[ConditionalInvocationQueryMixin.OUTPUT_DIR_ATTRIBUTE_NAME],
            preserve_dir_structure=metadata.pop("preserve_dir_structure"),
        )

        metadata[MultipleOutputProcessorMixin.ATTRIBUTE_NAME] = list(
            itertools.chain(*metadata[self.__class__._FILENAME_MAP_ATTRIBUTE_NAME].values()),  # pylint: disable=protected-access
        )

        return super(CodeGenerator, self)._CreateContext(dm, metadata)

    # ----------------------------------------------------------------------
    @overridemethod
    def _InvokeImpl(
        self,
        invoke_reason: InvokeReason,
        dm: DoneManager,
        context: dict[str, Any],
        on_progress_func: Callable[
            [
                int,                        # Step (0-based)
                str,                        # Status
            ],
            bool,                           # True to continue, False to terminate
        ],
    ) -> Optional[str]:                     # Optional short description that provides input about the result
        plugin = self.GetPlugin(context)

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

        # Parse
        results = Parse(
            dm,
            {
                input_root: workspace_files,
            },
            single_threaded=False,
            quiet=False,
            raise_if_single_exception=False,
        )

        assert len(results) == 1
        results = next(iter(results.values()))

        if dm.result != 0:
            exceptions: dict[Path, Exception] = {
                key: value
                for key, value in results.items()
                if isinstance(value, Exception)
            }

            assert exceptions

            _PrintExceptions(dm, exceptions)

            return None

        roots = cast(dict[Path, RootStatement], results)

        # Resolve
        results = Resolve(
            dm,
            roots,
            single_threaded=False,
            quiet=False,
            raise_if_single_exception=False,
        )

        if dm.result != 0:
            assert results is not None
            assert all(isinstance(result, Exception) for result in results.values())

            _PrintExceptions(dm, cast(dict[Path, Exception], results))

            return None

        # Normalize
        flags = plugin.flags

        for context_name, flag in [
            ("filter_unsupported_extensions", NormalizeFlag.DisableUnsupportedExtensions),
            ("filter_unsupported_metadata", NormalizeFlag.DisableUnsupportedMetadata),
            ("filter_unsupported_root_elements", NormalizeFlag.DisableUnsupportedRootElements),
            ("filter_unsupported_nested_elements", NormalizeFlag.DisableUnsupportedNestedElements),
        ]:
            if context.get(context_name, False):
                flags |= flag

        results = Normalize(
            dm,
            roots,
            plugin.metadata_attributes,
            plugin.extension_names,
            flags,
            single_threaded=False,
            quiet=False,
            raise_if_single_exception=False,
        )

        if dm.result != 0:
            assert results is not None
            assert all(isinstance(result, Exception) for result in results.values())

            _PrintExceptions(dm, cast(dict[Path, Exception], results))

            return None

        # Validate
        on_progress_func(CodeGenerator._Steps.Validating.value, "Validating...")

        # ----------------------------------------------------------------------
        def Validate(
            filename: Path,                             # pylint: disable=unused-argument
            root: RootStatement,
            on_status_func: Callable[[str], None],      # pylint: disable=unused-argument
        ) -> None:
            plugin.Validate(root)

        # ----------------------------------------------------------------------

        _ExecuteInParallel(
            dm,
            "Validating",
            roots,
            Validate,
        )

        if dm.result < 0:
            return None

        # Extract the context info requested by the plugin
        plugin_context: dict[str, Any] = {}

        for attribute_name in plugin.GetCommandLineArgs().keys():
            context_value = context.get(attribute_name, DoesNotExist.instance)
            if context_value is DoesNotExist.instance:
                continue

            plugin_context[attribute_name] = context_value

        # Generate
        on_progress_func(CodeGenerator._Steps.Generating.value, "Generating...")

        # ----------------------------------------------------------------------
        def GenerateCode(
            filename: Path,
            root: RootStatement,
            on_status_func: Callable[[str], None],
        ) -> None:
            key = context[AtomicInputProcessorMixin.INPUT_ROOT_ATTRIBUTE_NAME] / filename
            assert key in context[self.__class__._FILENAME_MAP_ATTRIBUTE_NAME], key  # pylint: disable=protected-access

            plugin.Generate(
                plugin_context,
                root,
                context[self.__class__._FILENAME_MAP_ATTRIBUTE_NAME][key],  # pylint: disable=protected-access
                on_status_func,
            )

        # ----------------------------------------------------------------------

        _ExecuteInParallel(
            dm,
            "Generating",
            roots,
            GenerateCode,
        )

        if dm.result < 0:
            return None

        return None


# ----------------------------------------------------------------------
_code_generator                             = CodeGenerator()


# ----------------------------------------------------------------------
def _HelpEpilog() -> str:
    return textwrap.dedent(
        """\
        [bold]Plugins[/]

        These plugins are enabled by default:

        {}
        """,
    ).format(
        TextwrapEx.CreateTable(
            [
                "Name",
                "Description",
            ],
            [
                [
                    "{}) {}".format(index + 1, plugin.name),
                    plugin.description
                ]
                for index, plugin in enumerate(_code_generator.EnumPlugins())
            ],
        ),
    ).replace("\n", "\n\n")


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
    rich_markup_mode="rich",
    epilog=_HelpEpilog(),
)


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
Generate                                    = CreateGenerateCommandLineFunc(app, _code_generator, process_plugin_args=True)
Clean                                       = CreateCleanCommandLineFunc(app, _code_generator, process_plugin_args=True)
List                                        = CreateListCommandLineFunc(app, _code_generator, process_plugin_args=True)


# ----------------------------------------------------------------------
# |
# |  Private Functions
# |
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
def _ExecuteInParallel(
    dm: DoneManager,
    heading: str,
    roots: dict[Path, RootStatement],
    func: Callable[[Path, RootStatement, Callable[[str], None]], None],
) -> None:
    # ----------------------------------------------------------------------
    def Execute(
        context: tuple[Path, RootStatement],
        status: ExecuteTasks.Status,
    ) -> None:
        filename, root = context
        del context

        func(
            filename,
            root,
            lambda value: cast(None, status.OnProgress(None, value)),
        )

    # ----------------------------------------------------------------------

    results = ExecuteInParallelImpl(
        dm,
        heading,
        {
            filename: (filename, root)
            for filename, root in roots.items()
        },
        Execute,
        quiet=False,
        max_num_threads=None,
        raise_if_single_exception=False,
    )

    if isinstance(results, dict) and isinstance(next(iter(results.values())), Exception):
        _PrintExceptions(dm, cast(dict[Path, Exception], results))


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app()
