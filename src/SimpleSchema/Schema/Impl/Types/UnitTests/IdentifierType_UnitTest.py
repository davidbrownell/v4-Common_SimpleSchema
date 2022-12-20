# ----------------------------------------------------------------------
# |
# |  IdentifierType_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-15 11:15:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for IdentifierType.py"""

import re
import sys

from pathlib import Path
from unittest import mock

import pytest

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent.parent.parent.parent)))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchema.Schema.Impl.Common.Identifier import Identifier, SimpleElement, Visibility
    from SimpleSchema.Schema.Impl.Common.Range import Range
    from SimpleSchema.Schema.Impl.Common.SimpleSchemaException import SimpleSchemaException
    from SimpleSchema.Schema.Impl.Types.IdentifierType import IdentifierType


# ----------------------------------------------------------------------
def test_SingleIdentifier():
    range1 = mock.MagicMock()
    range2 = mock.MagicMock()
    cardinality_mock = mock.MagicMock()

    i = IdentifierType(
        range1,
        cardinality_mock,
        None,
        [
            Identifier(
                range2,
                SimpleElement(mock.MagicMock(), "TheType"),
                SimpleElement(mock.MagicMock(), Visibility.Private),
            ),
        ],
        None,
    )

    assert i.range is range1
    assert i.cardinality is cardinality_mock
    assert i.metadata is None

    assert len(i.identifiers) == 1
    assert i.identifiers[0].range is range2
    assert i.identifiers[0].id.value == "TheType"
    assert i.identifiers[0].visibility.value == Visibility.Private

    assert i.element_reference is None


# ----------------------------------------------------------------------
def test_MultipleIdentifiers():
    range = mock.MagicMock()
    cardinality = mock.MagicMock()
    metadata = mock.MagicMock()
    id1 = mock.MagicMock()
    id2 = mock.MagicMock()

    i = IdentifierType(
        range,
        cardinality,
        metadata,
        [id1, id2],
        None,
    )

    assert i.range is range
    assert i.cardinality is cardinality
    assert i.metadata is metadata
    assert i.identifiers == [id1, id2]
    assert i.element_reference is None


# ----------------------------------------------------------------------
def test_WithElementReference():
    reference_range = mock.MagicMock()

    i = IdentifierType(mock.MagicMock(), mock.MagicMock(), mock.MagicMock(), [mock.MagicMock()], reference_range)

    assert i.element_reference is reference_range


# ----------------------------------------------------------------------
def test_ErrorInvalid():
    for invalid_value in [
        "invalidValue",
        "_invalidValue",
    ]:
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("'{}' is not a valid type; identifier types must begin with an uppercase letter. (file_for_invalid_content <[1, 2] -> [3, 4]>)".format(invalid_value)),
        ):
            IdentifierType(
                mock.MagicMock(),
                mock.MagicMock(),
                None,
                [
                    Identifier(
                        mock.MagicMock(),
                        SimpleElement(Range.Create(Path("file_for_invalid_content"), 1, 2, 3, 4), invalid_value),
                        SimpleElement(mock.MagicMock(), mock.MagicMock()),
                    ),
                ],
                None,
            )

        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("'{}' is not a valid type; identifier types must begin with an uppercase letter. (file_for_invalid_content <[2, 4] -> [6, 8]>)".format(invalid_value)),
        ):
            IdentifierType(
                mock.MagicMock(),
                mock.MagicMock(),
                None,
                [
                    Identifier(
                        mock.MagicMock(),
                        SimpleElement(mock.MagicMock(), "ValidValue"),
                        SimpleElement(mock.MagicMock(), mock.MagicMock()),
                    ),
                    Identifier(
                        mock.MagicMock(),
                        SimpleElement(Range.Create(Path("file_for_invalid_content"), 2, 4, 6, 8), invalid_value),
                        SimpleElement(mock.MagicMock(), mock.MagicMock()),
                    ),
                ],
                None,
            )


# ----------------------------------------------------------------------
def test_ErrorNoIdentifiers():
    with pytest.raises(
        SimpleSchemaException,
        match=re.escape("'IdentifierType' instances must have at least one identifier. (filename <[11, 22] -> [33, 44]>)"),
    ):
        IdentifierType(
            Range.Create(Path("filename"), 11, 22, 33, 44),
            mock.MagicMock(),
            None,
            [],
            None,
        )


# ----------------------------------------------------------------------
def test_VisibilityErrors():
    for visibility, desc in [
        (Visibility.Private, "private"),
        (Visibility.Protected, "protected"),
    ]:
        # The first element can be private/protected
        IdentifierType(
            mock.MagicMock(),
            mock.MagicMock(),
            None,
            [
                Identifier(
                    mock.MagicMock(),
                    SimpleElement(mock.MagicMock(), "ValidType"),
                    SimpleElement(mock.MagicMock(), visibility),
                ),
            ],
            None,
        )

        # Subsequent identifiers may not be
        with pytest.raises(
            SimpleSchemaException,
            match=re.escape("'InvalidType' is {} and cannot be accessed. (error_filename <[10, 20] -> [30, 40]>)".format(desc)),
        ):
            IdentifierType(
                mock.MagicMock(),
                mock.MagicMock(),
                None,
                [
                    Identifier(
                        mock.MagicMock(),
                        SimpleElement(mock.MagicMock(), "ValidType"),
                        SimpleElement(mock.MagicMock(), visibility),
                    ),
                    Identifier(
                        mock.MagicMock(),
                        SimpleElement(mock.MagicMock(), "InvalidType"),
                        SimpleElement(
                            Range.Create(Path("error_filename"), 10, 20, 30, 40),
                            visibility,
                        ),
                    ),
                ],
                None,
            )
