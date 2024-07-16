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

import re
import typing

import pytest

from jera import frozen


class FrozenClass(metaclass=frozen.FrozenMeta):
    def __init__(self) -> None:
        self.frozen_attr = 123


class UnfrozenClass(metaclass=frozen.FrozenMeta):
    __frozen__ = False

    def __init__(self) -> None:
        self.unfrozen_attr = 321


@pytest.fixture(name="new_frozen_instance")
def _new_frozen_instance() -> FrozenClass:
    frozen_instance = FrozenClass()
    return frozen_instance


@pytest.fixture(name="new_unfrozen_instance")
def _new_unfrozen_instance() -> UnfrozenClass:
    unfrozen_instance = UnfrozenClass()
    return unfrozen_instance


class TestFrozen:
    def test___init___on_frozen_instance(
        self, new_frozen_instance: FrozenClass,
    ) -> None:
        assert new_frozen_instance.frozen_attr == 123

    def test_instance_is_frozen_by_default(
        self, new_frozen_instance: FrozenClass,
    ) -> None:
        with pytest.raises(
            frozen.FrozenInstanceError,
            match=f"{new_frozen_instance!r} instance is frozen."
        ):
            new_frozen_instance.frozen_attr = 123321

    def test_instance_frozen_override(
        self, new_unfrozen_instance: UnfrozenClass,
    ) -> None:
        new_unfrozen_instance.unfrozen_attr = 321321
        assert new_unfrozen_instance.unfrozen_attr == 321321

    def test_frozen_instance_invalid_override(self) -> None:
        frozen_value = 2134523412
        with pytest.raises(
            ValueError,
            match=(
                f"__frozen__ expected a boolean value, "
                f"but {type(frozen_value)}/{frozen_value} received."
            )
        ):
            class _UnfrozenClass(metaclass=frozen.FrozenMeta):
                __frozen__ = frozen_value

    def test_unfreeze_attrs_override(self) -> None:
        class FrozenClassOverride(metaclass=frozen.FrozenMeta):
            # __frozen__ is True by default
            __unfreeze_attrs__: typing.AbstractSet[str] = {
                "unfrozen_method",
            }

            def __init__(self) -> None:
                self.value = 123

            def unfrozen_method(self) -> None:
                self.value = 321

            def frozen_method(self) -> None:
                self.value = 321123

        frozen_instance_override = FrozenClassOverride()
        with pytest.raises(
            frozen.FrozenInstanceError,
            match=f"{frozen_instance_override!r} instance is frozen."
        ):
            frozen_instance_override.frozen_method()

        assert frozen_instance_override.value == 123
        frozen_instance_override.unfrozen_method()
        assert frozen_instance_override.value == 321

    def test_unfreeze_attrs_invalid_override(self) -> None:
        unfreeze_attrs = ["unfrozen_method"]
        with pytest.raises(
            ValueError,
            match=re.escape(
                f"__unfreeze_attrs__ expected a set value, "
                f"but {type(unfreeze_attrs)}/{unfreeze_attrs} received."
            )
        ):
            class _UnfrozenClassOverride(metaclass=frozen.FrozenMeta):
                __unfreeze_attrs__ = unfreeze_attrs
