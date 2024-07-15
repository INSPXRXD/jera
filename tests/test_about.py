# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2024 INSPXRXD
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from __future__ import annotations

import pytest

from jera import __about__


class TestVersion:
    def test_version_from_str(self) -> None:
        version = __about__.Version.from_str(
            __about__.__version__
        )
        assert isinstance(version.major, int)
        assert isinstance(version.minor, int)
        assert isinstance(version.serial, int)
        assert isinstance(version.stage, (str, type(None)))

    def test_version_is_final(self) -> None:
        version = __about__.Version(
            major=123,
            minor=321,
            serial=0,
            stage=None,
        )
        assert version.is_final()

    def test_version_final(self) -> None:
        version = __about__.Version.from_str(
            __about__.__version__
        )
        if version.is_final():
            assert version.stage is None
            assert version.serial == 0

    @pytest.mark.parametrize(
        "version_str, expected",
        [
            ("1.0a1", __about__.Version(major=1, minor=0, stage="a", serial=1)),
            ("2.3b2", __about__.Version(major=2, minor=3, stage="b", serial=2)),
            ("3.1rc3", __about__.Version(major=3, minor=1, stage="rc", serial=3)),
        ]
    )
    def test_from_str_indev(
        self,
        version_str: str,
        expected: __about__.Version,
    ) -> None:
        assert __about__.Version.from_str(version_str) == expected

    @pytest.mark.parametrize(
        "version_str, expected",
        [
            ("1.0", __about__.Version(major=1, minor=0, stage=None, serial=0)),
            ("2.3", __about__.Version(major=2, minor=3, stage=None, serial=0)),
        ]
    )
    def test_from_str_final(
        self,
        version_str: str,
        expected: __about__.Version,
    ) -> None:
        assert __about__.Version.from_str(version_str) == expected

    @pytest.mark.parametrize(
        "version_str",
        [
            "1.0a",  # Missing serial
            "2.3beta2",  # Invalid stage
            "3.1.rc1",  # Extra dot
            "1.0a-1",  # Invalid serial format
        ]
    )
    def test_from_str_invalid_indev(self, version_str: str) -> None:
        with pytest.raises(ValueError, match=f"Invalid version string: {version_str}"):
            __about__.Version.from_str(version_str)

    @pytest.mark.parametrize(
        "version_str",
        [
            "1",  # Missing minor version
            "2.3.",  # Extra dot at the end
            "1.0.0",  # Extra version (patch)
            "version1.0"  # Invalid format
        ]
    )
    def test_from_str_invalid_final(self, version_str: str) -> None:
        with pytest.raises(ValueError, match=f"Invalid version string: {version_str}"):
            __about__.Version.from_str(version_str)
