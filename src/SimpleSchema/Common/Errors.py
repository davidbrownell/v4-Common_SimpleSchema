# ----------------------------------------------------------------------
# |
# |  Errors.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-18 20:08:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains errors generated during the SimpleSchema process"""

from pathlib import Path
from typing import Tuple

from .Range import Range
from .SimpleSchemaException import DynamicSimpleSchemaException


# ----------------------------------------------------------------------
# pylint: disable=invalid-name


# ----------------------------------------------------------------------
# |
# |  ANTLR Parsing Errors
# |
# ----------------------------------------------------------------------
antlr_invalid_opening_token                 = "Triple-quote delimiters that initiate multiline strings cannot have any content on the same line."
antlr_invalid_closing_token                 = "Triple-quote delimiters that terminate multiline strings cannot have any content on the same line."
antlr_invalid_indentation                   = "Invalid multiline string indentation."

ParseCreateIncludeStatementDirWithStar      = DynamicSimpleSchemaException.CreateType("Filenames must be provided with wildcard imports; '{name}' is a directory.", name=Path)
ParseCreateIncludeStatementInvalidFilename  = DynamicSimpleSchemaException.CreateType("'{name}' is not a valid filename.", name=str)
ParseCreateIncludeStatementInvalidPath      = DynamicSimpleSchemaException.CreateType("'{name}' is not a valid filename or directory name.", name=Path)
ParseCreateIncludeStatementInvalidWorkspace = DynamicSimpleSchemaException.CreateType("The included file '{name}' is not a descendant of any workspace.", name=Path)
ParseCreateIncludeStatementTooManyItems     = DynamicSimpleSchemaException.CreateType("A single filename must be imported when including content from a directory.")

ParseStructureStatementInvalidBase          = DynamicSimpleSchemaException.CreateType("Base types must be an identifier or a tuple that contains identifiers.")
ParseStructureStatementInvalidTupleBaseItem = DynamicSimpleSchemaException.CreateType("Tuple base types may only contain identifiers.")

# ----------------------------------------------------------------------
# |
# |  Element Construction Errors
# |
# ----------------------------------------------------------------------
CardinalityInvalidMetadata                  = DynamicSimpleSchemaException.CreateType("Metadata cannot be associated with single elements.")
CardinalityInvalidRange                     = DynamicSimpleSchemaException.CreateType("Invalid cardinality ({min} > {max}).", min=int, max=min)

ExtensionStatementDuplicateKeywordArg       = DynamicSimpleSchemaException.CreateType("An argument for the parameter '{name}' was already provided at '{range}'.", name=str, range=Range)

MetadataItemDuplicated                      = DynamicSimpleSchemaException.CreateType("The metadata item '{key}' has already been provided at {prev_range}.", key=str, prev_range=Range)

NamespaceCycle                              = DynamicSimpleSchemaException.CreateType("A cycle was detected in the definition of '{name}':\n\n{ancestors_str}", name=str, ancestors_str=str, ancestors=list[Tuple[str, Range]])
NamespaceDuplicateTypeName                  = DynamicSimpleSchemaException.CreateType("The type '{name}' has already been defined at '{original_range}'.", name=str, original_range=Range)
NamespaceFundamentalItemReference           = DynamicSimpleSchemaException.CreateType("Item references to fundamental types are not valid (as they are already item references).")
NamespaceInvalidIncludeItem                 = DynamicSimpleSchemaException.CreateType("The included item '{name}' does not exist.", name=str)
NamespaceInvalidIncludeItemVisibility       = DynamicSimpleSchemaException.CreateType("The included item '{name}' exists but is not accessible due to its visibility.", name=str)
NamespaceInvalidType                        = DynamicSimpleSchemaException.CreateType("The type '{name}' was not found.", name=str)
NamespaceStructureItemReference             = DynamicSimpleSchemaException.CreateType("Item references to structures are not valid (as they are already item references).")
NamespaceVisibilityError                    = DynamicSimpleSchemaException.CreateType("The visibility 'protected' is not valid for root elements.")

ParseIdentifierNoChars                      = DynamicSimpleSchemaException.CreateType("'{id}' does not have any identifiable characters.", id=str)
ParseIdentifierNotAlpha                     = DynamicSimpleSchemaException.CreateType("The first identifiable character in '{id}' must be a letter.", id=str)

ParseIdentifierTypeEmpty                    = DynamicSimpleSchemaException.CreateType("Identifier types must have at least one identifier.")
ParseIdentifierTypeInvalidGlobal            = DynamicSimpleSchemaException.CreateType("There may only be one identifier for global types.")
ParseIdentifierTypeNotType                  = DynamicSimpleSchemaException.CreateType("'{id}' is not a valid type name.", id=str)

ParseIncludeStatementItemNotType            = DynamicSimpleSchemaException.CreateType("The imported element '{name}' is not a type.", name=str)
ParseIncludeStatementItemReferenceNotPublic = DynamicSimpleSchemaException.CreateType("'{name}' is not a type name.", name=str)

ParseIncludeStatementInvalidFile            = DynamicSimpleSchemaException.CreateType("'{name}' is not a valid file.", name=Path)
ParseIncludeStatementInvalidItems           = DynamicSimpleSchemaException.CreateType("No items were expected.")
ParseIncludeStatementMissingItems           = DynamicSimpleSchemaException.CreateType("Items were expected.")

ParseStructureStatementInvalidBaseCardinality   = DynamicSimpleSchemaException.CreateType("Base types must have a cardinality of 1.")

ParseTupleTypeMissingTypes                  = DynamicSimpleSchemaException.CreateType("No tuple types were provided.")

ParseVariantTypeMissingTypes                = DynamicSimpleSchemaException.CreateType("Not enough types were provided.")
ParseVariantTypeNestedType                  = DynamicSimpleSchemaException.CreateType("Nested variant types are not supported.")

RootStatementInvalidNested                  = DynamicSimpleSchemaException.CreateType("Root statements may not be nested.")

StructureStatementInvalidSingleBase         = DynamicSimpleSchemaException.CreateType("Base classes must be fundamental or structure types when a single base class is specified.")
StructureStatementInvalidBase               = DynamicSimpleSchemaException.CreateType("Base classes must be structure types when multiple base classes are specified.")

TupleExpressionNoExpressions                = DynamicSimpleSchemaException.CreateType("No expressions were provided.")

TupleTypeNoTypes                            = DynamicSimpleSchemaException.CreateType("No types were provided.")
TupleTypeTupleExpressionExpected            = DynamicSimpleSchemaException.CreateType("A tuple expression was expected.")

VariantTypeCardinality                      = DynamicSimpleSchemaException.CreateType("Types nested within a variant cannot specify cardinality when the variant specifies cardinality as well; either remove cardinality values from all nested items or remove the cardinality from the variant itself.")
VariantTypeNested                           = DynamicSimpleSchemaException.CreateType("Variant types may not be nested within variant types.")
VariantTypeNotEnoughTypes                   = DynamicSimpleSchemaException.CreateType("At least two types must be provided.")
VariantTypeInvalidValue                     = DynamicSimpleSchemaException.CreateType("The expression '{expression}' does not produce a value that corresponds to any types within '{type}'.", expression=str, type=str)


# ----------------------------------------------------------------------
# |
# |  Resolve Errors
# |
# ----------------------------------------------------------------------
ResolveStructureStatementWithCardinality    = DynamicSimpleSchemaException.CreateType("Structure statements cannot specify a cardinality value.")
ResolveStructureStatementEmptyPseudoElement = DynamicSimpleSchemaException.CreateType("Pseudo structure definitions must contain at least one child.")


# ----------------------------------------------------------------------
# |
# |  Type Errors
# |
# ----------------------------------------------------------------------
cardinality_validate_list_required          = "A list of items was expected."
cardinality_validate_list_not_expected      = "A list of items was not expected."
cardinality_validate_list_too_large         = "No more than {value} {value_verb} expected ({found} {found_verb} found)."
cardinality_validate_list_too_small         = "At least {value} {value_verb} expected ({found} {found_verb} found)."
cardinality_validate_none_not_expected      = "None was not expected."

directory_type_invalid_dir                  = "'{value}' is not a valid directory."

enum_type_invalid_value                     = "'{value}' is not a valid enum value."

fundamental_type_creator_invalid_type       = "'{value}' is not a supported python type."

filename_type_does_not_exist                = "'{value}' is not a valid filename or directory."
filename_type_invalid_file                  = "'{value}' is not a valid filename."

integer_type_too_large                      = "'{value}' is greater than '{constraint}'."
integer_type_too_small                      = "'{value}' is less than '{constraint}'."

string_type_regex_failure                   = "The value '{value}' does not match the regular expression '{expression}'."
string_type_too_large                       = "No more than {value} {value_verb} expected ({found} {found_verb} found)."
string_type_too_small                       = "At least {value} {value_verb} expected ({found} {found_verb} found)."

tuple_type_item_mismatch                    = "{value} {value_verb} expected ({found} {found_verb} found)."

type_validate_invalid_python_type           = "A python '{python_type}' value cannot be converted into a '{type}' type."

uri_type_invalid_value                      = "'{value}' is not a valid URI."

variant_type_invalid_value                  = "The python '{python_type}' value does not correspond to any types within '{type}'."
