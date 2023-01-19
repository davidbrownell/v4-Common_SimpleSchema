# ----------------------------------------------------------------------
# |
# |  Plugin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-14 14:58:37
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
from contextlib import contextmanager
from enum import auto, IntFlag
from pathlib import Path
from typing import Callable, Iterator, List, Optional, Protocol, Set

from Common_Foundation.Types import extensionmethod

from Common_FoundationEx.CompilerImpl.PluginBase import PluginBase

from SimpleSchema.Schema.Elements.Statements.ExtensionStatement import ExtensionStatement
from SimpleSchema.Schema.Elements.Statements.ItemStatement import ItemStatement
from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement
from SimpleSchema.Schema.Elements.Statements.StructureStatement import StructureStatement

from SimpleSchema.Schema.MetadataAttributes.MetadataAttribute import MetadataAttribute

from SimpleSchema.Schema.Visitors.Visitor import VisitResult


# ----------------------------------------------------------------------
class Plugin(PluginBase):
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

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        flags: Flag,
        custom_extension_names: Optional[Set[str]],
        custom_metadata_attributes: Optional[List[MetadataAttribute]],
    ):
        assert custom_extension_names is None or custom_extension_names
        assert custom_metadata_attributes is None or custom_metadata_attributes

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
        input_filenames: Path,
        output_dir: Path,
        *,
        preserve_dir_structure: bool,
    ) -> dict[Path, list[Path]]:
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnExtensionStatement(
        self,
        extension: ExtensionStatement,  # pylint: disable=unused-argument
    ) -> Iterator[Optional[VisitResult]]:
        """Process the extension statement"""

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnItemStatement(
        self,
        item: ItemStatement,  # pylint: disable=unused-argument
    ) -> Iterator[Optional[VisitResult]]:
        """Process the item statement"""

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    @extensionmethod
    def OnStructureStatement(
        self,
        structure: StructureStatement,  # pylint: disable=unused-argument
    ) -> Iterator[Optional[VisitResult]]:
        """Process the structure statement"""

        yield

    # ----------------------------------------------------------------------
    @abstractmethod
    def Generate(
        self,
        output_filenames: list[Path],
        root: RootStatement,
        on_status_update_func: Callable[[str], None],
    ) -> None:
        """Generate the output for the plugin"""

        raise Exception("Abstract method")

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
        filename_decorator: _InputFilenameToOutputFilenames_FilenameDecorator,
        *,
        preserve_dir_structure: bool,
    ) -> dict[Path, list[Path]]:
        filename_map: dict[Path, list[Path]] = {}

        if preserve_dir_structure:
            len_input_root = len(input_root.parts)

            for input_filename in input_filenames:
                filename_map[input_filename] = filename_decorator(
                    input_filename,
                    output_dir / Path(*input_filename.parts[len_input_root:]),
                )

        else:
            filename_lookup: dict[Path, Path] = {}

            for input_filename in input_filenames:
                output_filenames = filename_decorator(
                    input_filename,
                    output_dir / input_filename.name,
                )

                for output_filename in output_filenames:
                    existing_input_filename = filename_lookup.get(output_filename, None)

                    if existing_input_filename is not None:
                        raise Exception(
                            "The output file '{}' generated by the input '{}' would be overwritten by the output file generated by the input '{}'.".format(
                                output_filename,
                                existing_input_filename,
                                input_filename,
                            ),
                        )

                    filename_lookup[output_filename] = input_filename

                filename_map[input_filename] = output_filenames

        return filename_map
