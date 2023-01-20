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

from .Range import Range
from .SimpleSchemaException import CreateExceptionType


# ----------------------------------------------------------------------
# |
# |  ANTLR Parsing Errors
# |
# ----------------------------------------------------------------------
AntlrInvalidOpeningToken                    = "Triple-quote delimiters that initiate multiline strings cannot have any content on the same line."       # pylint: disable=invalid-name
AntlrInvalidClosingToken                    = "Triple-quote delimiters that terminate multiline strings cannot have any content on the same line."      # pylint: disable=invalid-name
AntlrInvalidIndentation                     = "Invalid multiline string indentation."                                                                   # pylint: disable=invalid-name

ParseCreateIncludeStatementDirWithStar      = CreateExceptionType("Filenames must be provided with wildcard imports; '{name}' is a directory.", name=Path)
ParseCreateIncludeStatementInvalidFilename  = CreateExceptionType("'{name}' is not a valid filename.", name=str)
ParseCreateIncludeStatementInvalidPath      = CreateExceptionType("'{name}' is not a valid filename or directory name.", name=Path)
ParseCreateIncludeStatementInvalidWorkspace = CreateExceptionType("The included file '{name}' is not a descendant of any workspace.", name=Path)
ParseCreateIncludeStatementTooManyItems     = CreateExceptionType("A single filename must be imported when including content from a directory.")

ParseStructureStatementInvalidBase          = CreateExceptionType("Base types must be identifiers or a tuple that contains identifiers.")
ParseStructureStatementInvalidTupleBaseItem = CreateExceptionType("Tuple base types may only contain identifiers.")

# ----------------------------------------------------------------------
# |
# |  Element Construction Errors
# |
# ----------------------------------------------------------------------
CardinalityInvalidMetadata                  = CreateExceptionType("Metadata cannot be associated with single elements.")
CardinalityInvalidRange                     = CreateExceptionType("Invalid cardinality ({min} > {max}).", min=int, max=min)

ExtensionStatementDuplicateKeywordArg       = CreateExceptionType("An argument for the parameter '{name}' was already provided at '{range}'.", name=str, range=Range)

MetadataItemDuplicated                      = CreateExceptionType("The metadata item '{key}' has already been provided at {prev_range}.", key=str, prev_range=Range)

ParseIdentifierNoChars                      = CreateExceptionType("'{id}' does not have any identifiable characters.", id=str)
ParseIdentifierNotAlpha                     = CreateExceptionType("The first identifiable character in '{id}' must be a letter.", id=str)

ParseIdentifierTypeEmpty                    = CreateExceptionType("Identifier types must have at least one identifier.")
ParseIdentifierTypeInvalidGlobal            = CreateExceptionType("There may only be one identifier for global types.")
ParseIdentifierTypeNotType                  = CreateExceptionType("'{id}' is not a valid type name.", id=str)

ParseIncludeStatementItemNotPublic          = CreateExceptionType("The imported element '{name}' is not a public type.", name=str)
ParseIncludeStatementItemNotType            = CreateExceptionType("The imported element '{name}' is not a type.", name=str)
ParseIncludeStatementItemReferenceNotPublic = CreateExceptionType("'{name}' is not a type name.", name=str)

ParseIncludeStatementInvalidFile            = CreateExceptionType("'{name}' is not a valid file.", name=Path)
ParseIncludeStatementInvalidItems           = CreateExceptionType("No items were expected.")
ParseIncludeStatementMissingItems           = CreateExceptionType("Items were expected.")

ParseStructureStatementInvalidBaseCardinality   = CreateExceptionType("Base types must have a cardinality of 1.")

ParseTupleTypeMissingTypes                  = CreateExceptionType("No tuple types were provided.")

ParseVariantTypeMissingTypes                = CreateExceptionType("Not enough types were provided.")
ParseVariantTypeNestedType                  = CreateExceptionType("Nested variant types are not supported.")

RootStatementInvalidNested                  = CreateExceptionType("Root statements may not be nested.")

TupleExpressionNoExpressions                = CreateExceptionType("No expressions were provided.")
