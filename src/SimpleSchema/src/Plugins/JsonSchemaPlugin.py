# ----------------------------------------------------------------------
# |
# |  JsonSchemaPlugin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-02 14:56:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the JsonSchema plugin object"""

from pathlib import Path
from typing import Any, Callable

from Common_Foundation.Types import overridemethod

from Common_FoundationEx import TyperEx


# ----------------------------------------------------------------------
# pylint: disable=import-error
from SimpleSchema.Plugin import Plugin as PluginBase

from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement


# ----------------------------------------------------------------------
class Plugin(PluginBase):  # pylint: disable=missing-class-docstring

    # ----------------------------------------------------------------------
    # |
    # |  Public Properties
    # |
    # ----------------------------------------------------------------------
    @property
    @overridemethod
    def name(self) -> str:
        return "JsonSchema"

    @property
    @overridemethod
    def description(self) -> str:
        return "Generates a JSON Schema."

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(Plugin, self).__init__(
            flags=(
                PluginBase.Flag.AllowRootItems
                | PluginBase.Flag.AllowRootStructures
                | PluginBase.Flag.AllowNestedItems
                | PluginBase.Flag.AllowNestedStructures
                | PluginBase.Flag.CreateDottedNames
                | PluginBase.Flag.ResolveMetadata
            ),
            custom_extension_names=None,
            custom_metadata_attributes=None,
        )

    # ----------------------------------------------------------------------
    @overridemethod
    def GetCommandLineArgs(self) -> TyperEx.TypeDefinitionsType:
        return {} # T_O_D_O

    # ----------------------------------------------------------------------
    @overridemethod
    def GetNumAdditionalSteps(
        self,
        context: dict[str, Any],  # pylint: disable=unused-argument
    ) -> int:
        return 0

    # ----------------------------------------------------------------------
    @overridemethod
    def GenerateOutputFilenames(
        self,
        input_root: Path,
        input_filenames: list[Path],
        output_dir: Path,
        *,
        preserve_dir_structure: bool,
    ) -> dict[Path, list[Path]]:
        return self.__class__._InputFilenameToOutputFilenames(  # pylint: disable=protected-access
            input_root,
            input_filenames,
            output_dir,
            lambda input_filename, default_output_filename: [default_output_filename.with_suffix(".schema.json"), ],
            preserve_dir_structure=preserve_dir_structure,
        )

    # ----------------------------------------------------------------------
    # T_O_D_O: pylint: disable=unused-argument
    # T_O_D_O: pylint: disable=unused-variable
    @overridemethod
    def Generate(
        self,
        root: RootStatement,
        output_filenames: list[Path],
        on_status_update_func: Callable[[str], None],  # pylint: disable=unused-argument
    ) -> None:
        assert len(output_filenames) == 1
        output_filename = output_filenames[0]
        del output_filenames

        # T_O_D_O: Finish
