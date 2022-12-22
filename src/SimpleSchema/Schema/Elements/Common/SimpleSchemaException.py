# ----------------------------------------------------------------------
# |
# |  SimpleSchemaException.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-14 16:37:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the SimpleSchemaException object"""

from SimpleSchema.Schema.Elements.Common.Range import Range


# ----------------------------------------------------------------------
class SimpleSchemaException(Exception):
    """Exception raise during simple schema parsing and validation"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        msg: str,
        range_value: Range,
    ) -> None:
        super(SimpleSchemaException, self).__init__("{} ({})".format(msg, range_value.ToString()))

        self.range                          = range_value
