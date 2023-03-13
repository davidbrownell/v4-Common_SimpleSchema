# ----------------------------------------------------------------------
# |
# |  ParseState.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-03-13 07:23:20
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParseState object"""

import threading

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator

from .Impl.ReferenceCounts import ReferenceCounts


# ----------------------------------------------------------------------
@dataclass
class ParseState(object):
    """Information maintained throughout the parsing process"""

    # ----------------------------------------------------------------------
    _reference_counts: ReferenceCounts      = field(init=False, default_factory=ReferenceCounts)
    _reference_counts_lock: threading.Lock  = field(init=False, default_factory=threading.Lock)
    _reference_counts_finalized: bool       = field(init=False, default=False)

    # ----------------------------------------------------------------------
    @property
    def reference_counts(self) -> ReferenceCounts:
        assert self._reference_counts_finalized is True
        return self._reference_counts

    # ----------------------------------------------------------------------
    @contextmanager
    def YieldReferenceCounts(self) -> Iterator[ReferenceCounts]:
        with self._reference_counts_lock:
            yield self._reference_counts

    # ----------------------------------------------------------------------
    def FinalizeReferenceCounts(self):
        self._reference_counts_finalized = True
