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

import os

from enum import auto, Enum
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple

import typer

from typer.core import TyperGroup

from Common_Foundation.Streams.DoneManager import DoneManager, DoneManagerException
from Common_Foundation.Types import overridemethod

from Common_FoundationEx.CompilerImpl.CodeGenerator import CodeGenerator as CodeGeneratorBase, CreateCleanCommandLineFunc, CreateGenerateCommandLineFunc, CreateListCommandLineFunc, InputType, InvokeReason
from Common_FoundationEx.CompilerImpl.Mixins.InputProcessorMixins.AtomicInputProcessorMixin import AtomicInputProcessorMixin
from Common_FoundationEx.CompilerImpl.Mixins.OutputProcessorMixins.MultipleOutputProcessorMixin import MultipleOutputProcessorMixin
from Common_FoundationEx.CompilerImpl.Mixins.PluginHostMixin import PluginHostMixin

from Common_FoundationEx import TyperEx


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
    PluginHostMixin,
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

        PluginHostMixin.__init__(self, plugin_host_init_args)

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
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    class _Steps(Enum):
        Parsing                             = 1
        Generating                          = auto()

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
        # BugBug: Should be 1 for parse and then N for generating
        return 1

    # ----------------------------------------------------------------------
    @overridemethod
    def _CreateContext(
        self,
        dm: DoneManager,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        if metadata["plugin"] == "None":
            raise DoneManagerException("Please specify a plugin.")

        # Convert the input filenames into output filenames
        preserve_dir_structure = metadata.pop("preserve_dir_structure")

        output_dir = metadata["output_dir"]

        if preserve_dir_structure:
            output_filenames: list[Path] = []

            if len(metadata[AtomicInputProcessorMixin.ATTRIBUTE_NAME]) == 1:
                output_filenames.append(output_dir / metadata[AtomicInputProcessorMixin.ATTRIBUTE_NAME][0].name)
            else:
                input_root = metadata[AtomicInputProcessorMixin.INPUT_ROOT_ATTRIBUTE_NAME]
                input_root_parts_len = len(input_root.parts)

                for input_filename in metadata[AtomicInputProcessorMixin.ATTRIBUTE_NAME]:
                    output_filenames.append(output_dir / Path(*input_filename.parts[input_root_parts_len:]))
        else:
            output_filenames_lookup: dict[Path, Path] = {}

            for input_filename in metadata[AtomicInputProcessorMixin.ATTRIBUTE_NAME]:
                output_filename = output_dir / input_filename.name

                existing_input_filename = output_filenames_lookup.get(output_filename, None)

                if existing_input_filename is not None:
                    raise Exception(
                        "The output file '{}' to be generated from the input file '{}' will be overwritten by the output file generated from the input file '{}'.".format(
                            output_filename,
                            existing_input_filename,
                            input_filename,
                        ),
                    )

                output_filenames_lookup[output_filename] = input_filename

            output_filenames = list(output_filenames_lookup.keys())

        # BugBug: Invoke plugin to figure out the output names

        metadata[MultipleOutputProcessorMixin.ATTRIBUTE_NAME] = output_filenames

        return super(CodeGenerator, self)._CreateContext(dm, metadata)

    # ----------------------------------------------------------------------
    @overridemethod
    def _InvokeImpl(
        self,
        invoke_reason: InvokeReason,
        dm: DoneManager,
        context: Dict[str, Any],
        on_progress_func: Callable[[int, str], bool,],
    ) -> Optional[str]:
        pass # BugBug


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
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app()
