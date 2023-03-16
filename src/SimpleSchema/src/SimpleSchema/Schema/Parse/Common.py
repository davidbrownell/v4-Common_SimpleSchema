# ----------------------------------------------------------------------
# |
# |  Common.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-03-16 13:17:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Common functionality shared by multiple stages of the parsing process"""


# ----------------------------------------------------------------------
# Include a couple of characters within the name that can'be be replicated
# when files are parsed (as they aren't supported). This should eliminate
# the change that someone will accidentally name an element this themselves.
PSEUDO_TYPE_NAME_PREFIX                     = "_PseudoType#^"
