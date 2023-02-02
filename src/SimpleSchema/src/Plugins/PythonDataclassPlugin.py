# ----------------------------------------------------------------------
# |
# |  PythonDataclassPlugin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-02 14:58:46
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

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, ClassVar

from Common_Foundation.Types import DoesNotExist, overridemethod

from Common_FoundationEx import TyperEx


# ----------------------------------------------------------------------
# pylint: disable=import-error
from SimpleSchema.Common.Range import Range
from SimpleSchema.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.MetadataAttribute import MetadataAttribute
from SimpleSchema.Plugin import Plugin as PluginBase

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Element import Element

from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement
from SimpleSchema.Schema.Elements.Statements.StructureStatement import StructureStatement

from SimpleSchema.Schema.Elements.Types.FundamentalTypes import AllFundamentalTypes
from SimpleSchema.Schema.Elements.Types.Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _MetadataAttributeBase(MetadataAttribute):  # pylint: disable=missing-class-docstring
    """Abstract base class for metadata attributes defined for use with this plugin."""

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                     = ""
    TYPE: ClassVar[Type]                    = DoesNotExist.instance  # type: ignore

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls) -> "MetadataAttribute":
        return cls(MetadataAttribute.Flag.Structure, cls.NAME, cls.TYPE)  # pylint: disable=too-many-function-args

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.NAME, "Make sure to define NAME."
        assert self.TYPE is not DoesNotExist.instance, "Make sure to define TYPE."

    # ----------------------------------------------------------------------
    @overridemethod
    def Validate(
        self,
        element: Element,
    ) -> None:
        if not (
            isinstance(element, StructureStatement)
            and element.name.value == "__Python__"
        ):
            raise SimpleSchemaException(
                element.range,
                "The attribute '{}' is not valid in this context.".format(self.name),
            )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ImportStatementsMetadataAttribute(_MetadataAttributeBase):
    """\
    Attribute for custom import statements.

    {
        import_statements: [
            "from foo import Bar",
            "import re",
        ]
    }
    """

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                     = "import_statements"

    TYPE: ClassVar[Type]                    = AllFundamentalTypes.StringType(
        Range.CreateFromCode(),
        Cardinality.CreateFromCode(1),
        None,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class CustomBaseClassesMetadataAttribute(_MetadataAttributeBase):
    """\
    Attribute containing base classes for the created class.

    {
        base_classes: ["Base1", "Base2", ]
    }
    """

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                     = "base_classes"

    TYPE: ClassVar[Type]                    = AllFundamentalTypes.StringType(
        Range.CreateFromCode(),
        Cardinality.CreateFromCode(1),
        None,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class CustomAttributesMetadataAttribute(_MetadataAttributeBase):
    """\
    Attribute for custom python attributes.

    {
        custom_attributes: [
            "value1: str",
            "value2: bool = field(kw_init=True)",
        ]
    }
    """

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                     = "custom_attributes"

    TYPE: ClassVar[Type]                    = AllFundamentalTypes.StringType(
        Range.CreateFromCode(),
        Cardinality.CreateFromCode(1),
        None,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class PostInitContentMetadataAttribute(_MetadataAttributeBase):
    '''\
    Custom post init content.

    {
        post_init_content:  """
                            More __post_init__ content here.
                            """
    }
    '''

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                     = "post_init_content"

    TYPE: ClassVar[Type]                    = AllFundamentalTypes.StringType(
        Range.CreateFromCode(),
        Cardinality.CreateFromCode(),
        None,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class CustomMethodsMetadataAttribute(_MetadataAttributeBase):
    '''
    Custom methods added to the generated class.

    {
        custom_methods: [
            """
            def Method1(self):
                ...
            """,

            """
            def Method2(self):
                ...
            """,
        ]
    }
    '''

    # ----------------------------------------------------------------------
    NAME: ClassVar[str]                     = "custom_methods"

    TYPE: ClassVar[Type]                    = AllFundamentalTypes.StringType(
        Range.CreateFromCode(),
        Cardinality.CreateFromCode(1),
        None,
    )

# ----------------------------------------------------------------------
class Plugin(PluginBase):
    # ----------------------------------------------------------------------
    # |
    # |  Public Properties
    # |
    # ----------------------------------------------------------------------
    @property
    @overridemethod
    def name(self) -> str:
        return "python_dataclass"

    @property
    @overridemethod
    def description(self) -> str:
        return "Generates Python dataclass objects."

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
