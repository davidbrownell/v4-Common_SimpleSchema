# ----------------------------------------------------------------------
# |
# |  Plugin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-30 10:08:31
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Plugin object"""

from abc import abstractmethod
from dataclasses import dataclass
from enum import auto, IntFlag
from pathlib import Path
from typing import Any, Callable, Optional, Protocol

from Common_FoundationEx.CompilerImpl.PluginBase import PluginBase

from .Common import Errors

from .MetadataAttribute import MetadataAttribute

from .Schema.Elements.Expressions.Expression import Expression

from .Schema.Elements.Statements.RootStatement import RootStatement


# ----------------------------------------------------------------------
class Plugin(PluginBase):
    """Plugin that generates content based on a SimpleSchema file (or files)"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class Flag(IntFlag):
        AllowRootItems                      = auto()
        AllowRootStructures                 = auto()

        AllowNestedItems                    = auto()
        AllowNestedStructures               = auto()

        CreateDottedNames                   = auto()
        ResolveMetadata                     = auto()

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ResolvedMetadata(object):
        expression: Expression
        python_value: Any

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        flags: Flag,
        custom_extension_names: Optional[set[str]],
        custom_metadata_attributes: Optional[list[MetadataAttribute]],
    ):
        if not (custom_extension_names is None or custom_extension_names):
            raise ValueError("custom_extension_names")
        if not (custom_metadata_attributes is None or custom_metadata_attributes):
            raise ValueError("custom_metadata_attributes")

        self.flags                          = flags
        self.custom_extension_names         = custom_extension_names or set()

        self.custom_metadata_attributes: dict[str, MetadataAttribute]       = {
            item.name: item
            for item in (custom_metadata_attributes or [])
        }

    # ----------------------------------------------------------------------
    @abstractmethod
    def GenerateOutputFilenames(
        self,
        input_root: Path,
        input_filenames: list[Path],
        output_dir: Path,
        *,
        preserve_dir_structure: bool,
    ) -> dict[Path, list[Path]]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    def Generate(
        self,
        root: RootStatement,
        output_filenames: list[Path],
        on_status_update_func: Callable[[str], None],
    ) -> None:
        """Generate output for the provided content"""

        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    class _InputFilenameToOutputFilenames_FilenameDecorator(Protocol):
        def __call__(
            self,
            input_filename: Path,
            default_output_filename: Path,
        ) -> list[Path]:
            ...

    @staticmethod
    def _InputFilenameToOutputFilenames(
        input_root: Path,
        input_filenames: list[Path],
        output_dir: Path,
        filename_decorator_func: _InputFilenameToOutputFilenames_FilenameDecorator,
        *,
        preserve_dir_structure: bool,
    ) -> dict[Path, list[Path]]:
        filename_map: dict[Path, list[Path]] = {}

        if preserve_dir_structure:
            len_input_root = len(input_root.parts)

            for input_filename in input_filenames:
                filename_map[input_filename] = filename_decorator_func(
                    input_filename,
                    output_dir / Path(*input_filename.parts[len_input_root:]),
                )

        else:
            filename_lookup: dict[Path, Path] = {}

            for input_filename in input_filenames:
                output_filenames = filename_decorator_func(
                    input_filename,
                    output_dir / input_filename.name,
                )

                for output_filename in output_filenames:
                    existing_input_filename = filename_lookup.get(output_filename, None)

                    if existing_input_filename is not None:
                        raise Exception(
                            Errors.plugin_duplicate_filename.format(
                                output_filename=output_filename,
                                existing_input_filename=existing_input_filename,
                                input_filename=input_filename,
                            ),
                        )

                    filename_lookup[output_filename] = input_filename

                filename_map[input_filename] = output_filenames

        return filename_map
