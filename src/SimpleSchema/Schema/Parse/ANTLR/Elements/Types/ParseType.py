# ----------------------------------------------------------------------
# |
# |  ParseType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 15:11:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseType object"""

from dataclasses import dataclass

from Common_Foundation.Types import overridemethod

from .....Elements.Types.Type import Type


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParseType(Type):
    """Temporary type generated during parsing and replaced during subsequent steps"""

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @overridemethod
    def _CloneImpl(self, *args, **kwargs):
        raise Exception("This should never be called on ParseType instances.")  # pragma: no cover
