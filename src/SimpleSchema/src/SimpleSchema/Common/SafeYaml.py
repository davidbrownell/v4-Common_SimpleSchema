# ----------------------------------------------------------------------
# |
# |  SafeYaml.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-02-08 13:28:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality to consistently dump yaml content"""

import sys
import threading
import yaml

from typing import Any  # pylint: disable=wrong-import-order

from Common_Foundation.ContextlibEx import ExitStack


# ----------------------------------------------------------------------
_global_monkey_patched_dumper               = None
_global_monkey_patched_dumper_lock          = threading.Lock()


# ----------------------------------------------------------------------
def ToYamlString(
    content: Any,
) -> str:
    global _global_monkey_patched_dumper  # pylint: disable=global-statement

    with _global_monkey_patched_dumper_lock:
        if _global_monkey_patched_dumper is None:
            _global_monkey_patched_dumper = _MonkeyPatchedDumper()

    return _global_monkey_patched_dumper(content)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _MonkeyPatchedDumper(object):
    # rtyaml is designed to round-trip python objects when yaml fails to do so. Unfortunately,
    # rtyaml hard-codes the loader and dumper used as a part of the process and the
    # hard-coded values are compiled binaries that look at content length to determine if
    # yaml complex keys are used or not. This introduces risk, as some content may be slightly
    # different on different machines (for example, filenames prior to scrubbing them for
    # consistency). This code will introduce monkey patches to ensure that rtyaml never
    # uses complex keys.

    # ----------------------------------------------------------------------
    def __init__(self):
        if "rtyaml" in sys.modules:
            raise Exception("This function must be called before rtyaml is imported.")

        # Monkey patch the content
        original_safe_loader = yaml.CSafeLoader
        original_dumper = yaml.CDumper

        yaml.CSafeLoader = yaml.SafeLoader
        yaml.CDumper = yaml.Dumper

        # ----------------------------------------------------------------------
        def RestorePatches():
            yaml.CSafeLoader = original_safe_loader
            yaml.CDumper = original_dumper

        # ----------------------------------------------------------------------

        with ExitStack(RestorePatches):
            import rtyaml

        # Create a dumper that never produces complex keys

        # ----------------------------------------------------------------------
        class CustomDumper(rtyaml.Dumper):
            """Dumper that forces the use of simple keys"""

            # ----------------------------------------------------------------------
            def __init__(self, *args, **kwargs):
                super(CustomDumper, self).__init__(
                    *args,
                    **{
                        **kwargs,
                        **{
                            "width": 100000,
                        },
                    },
                )

            # ----------------------------------------------------------------------
            def check_simple_key(self):
                # Always use simple keys
                return True

        # ----------------------------------------------------------------------
        def CustomDumpFunc(
            data,
            stream=None,
            Dumper=rtyaml.Dumper,  # pylint: disable=unused-argument
            **kwargs,
        ):
            return yaml.dump(data, stream, CustomDumper, **kwargs)

        # ----------------------------------------------------------------------

        self._dump_func = lambda content: rtyaml.do_dump(content, None, CustomDumpFunc)

    # ----------------------------------------------------------------------
    def __call__(self, content):
        return self._dump_func(content)
