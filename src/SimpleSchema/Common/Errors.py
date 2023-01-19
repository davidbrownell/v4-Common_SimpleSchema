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

from .Range import Range
from .SimpleSchemaException import CreateExceptionType


# ----------------------------------------------------------------------
# |
# |  ANTLR Parsing Errors
# |
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# |
# |  Element Construction Errors
# |
# ----------------------------------------------------------------------
DuplicateMetadataItem                       = CreateExceptionType("The metadata item '{key}' has already been provided at {prev_range}.", key=str, prev_range=Range)

InvalidCardinalityRange                     = CreateExceptionType("Invalid cardinality ({min} > {max}).", min=int, max=min)
InvalidCardinalityMetadata                  = CreateExceptionType("Metadata cannot be associated with single elements.")
