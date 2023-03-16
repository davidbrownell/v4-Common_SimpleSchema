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
from pathlib import Path
from typing import Any, Callable, Optional, Protocol

from Common_Foundation.Types import extensionmethod

from Common_FoundationEx.CompilerImpl.PluginBase import PluginBase

from .Common import Errors
from .Common.Range import Range

from .Schema.Elements.Common.SimpleElement import SimpleElement
from .Schema.Elements.Common.Visibility import Visibility

from .Schema.Elements.Statements.RootStatement import RootStatement

from .Schema.Elements.Types.ReferenceType import ReferenceType

from .Schema.MetadataAttributes.ContainerAttributes import PluralNameMetadataAttribute
from .Schema.MetadataAttributes.ElementAttributes import DefaultMetadataAttribute, DescriptionMetadataAttribute, NameMetadataAttribute
from .Schema.MetadataAttributes.MetadataAttribute import MetadataAttribute

from .Schema.Parse.Normalize.Normalize import Flag as NormalizeFlag


# ----------------------------------------------------------------------
class Plugin(PluginBase):
    """Plugin that generates content based on a SimpleSchema file (or files)"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    Flag                                    = NormalizeFlag

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        flags: NormalizeFlag,
        custom_extension_names: Optional[set[str]],
        custom_metadata_attributes: Optional[list[MetadataAttribute]],
    ):
        if not (custom_extension_names is None or custom_extension_names):
            raise ValueError("custom_extension_names")
        if not (custom_metadata_attributes is None or custom_metadata_attributes):
            raise ValueError("custom_metadata_attributes")

        metadata_attributes: list[MetadataAttribute] = [
            NameMetadataAttribute(),                    # pylint: disable=no-value-for-parameter
            DescriptionMetadataAttribute(),             # pylint: disable=no-value-for-parameter
            DefaultMetadataAttribute(),                 # pylint: disable=no-value-for-parameter
            PluralNameMetadataAttribute(),              # pylint: disable=no-value-for-parameter
        ]

        metadata_attributes += custom_metadata_attributes or []

        # For convenience, metadata attribute types are defined with BasicTypes and cardinality
        # values. Convert those values to actual types.
        for metadata_attribute in metadata_attributes:
            object.__setattr__(
                metadata_attribute,
                "_type",
                ReferenceType.Create(
                    SimpleElement[Visibility](metadata_attribute.type.range, Visibility.Private),
                    SimpleElement[str](metadata_attribute.type.range, "Type"),
                    metadata_attribute.type,
                    metadata_attribute.cardinality,
                    None,
                ),
            )

        self.flags                          = flags
        self.extension_names                = custom_extension_names or set()
        self.metadata_attributes            = metadata_attributes

    # ----------------------------------------------------------------------
    @extensionmethod
    def Validate(
        self,
        root: RootStatement,  # pylint: disable=unused-argument
    ) -> None:
        """Performs custom validation for the plugin"""

        # No custom validation by default
        pass

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
        command_line_args: dict[str, Any],
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
