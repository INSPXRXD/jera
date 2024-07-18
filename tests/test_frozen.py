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

import operator
import re
import typing

import pytest

from jera import frozen


@pytest.fixture(name="new_frozen_instance")
def _new_frozen_instance() -> FrozenClass:
    frozen_instance = FrozenClass()
    return frozen_instance


@pytest.fixture(name="new_thawable_instance")
def _new_thawable_instance() -> ThawableClass:
    thawable_instance = ThawableClass()
    return thawable_instance


class FrozenClass(frozen.Frozen):
    def __init__(self) -> None:
        self.frozen_attr = 123


class ThawableClass(frozen.Thawable):
    def __init__(self) -> None:
        self.thawable_attr = 123


class TestFrozen:
    def test_invalid_frozen_flag(self) -> None:
        frozen_flag = object
        with pytest.raises(
            ValueError,
            match=(
                f"__frozen__ expected a boolean value, "
                f"but {type(frozen_flag)}/{frozen_flag} received."
            ),
        ):
            class InvalidFrozenFlag(frozen.Frozen):
                __frozen__ = frozen_flag

    def test_frozen_glag_is_false(self) -> None:
        with pytest.raises(
            ValueError,
            match=(
                "__frozen__ cannot be builtins.False in "
                "a subclass of FrozenMeta."
            ),
        ):
            class InvalidFrozenFlag(frozen.Frozen):
                __frozen__ = False

    def test___init___on_frozen_instance(
        self, new_frozen_instance: FrozenClass,
    ) -> None:
        assert new_frozen_instance.frozen_attr == 123

    @pytest.mark.parametrize(
        "cls_mutator",
        [
            lambda cls: operator.setitem(cls, "a", "b"),
            lambda cls: setattr(cls, "c", "d"),
            lambda cls: operator.delitem(cls, "a"),
            lambda cls: delattr(cls, "b"),
        ],
    )
    def test_frozen_class_is_immutable(
        self,
        cls_mutator: typing.Callable[[typing.Type[typing.Any]], None],
    ) -> None:
        class _FrozenClass(frozen.Frozen):
            pass

        with pytest.raises(
            frozen.FrozenObjectError,
            match=f"Object {_FrozenClass!r} is frozen."
        ):
            cls_mutator(_FrozenClass)

    @pytest.mark.parametrize(
        "obj_mutator",
        [
            lambda obj: operator.setitem(obj, "a", "b"),
            lambda obj: setattr(obj, "c", "d"),
            lambda obj: operator.delitem(obj, "a"),
            lambda obj: delattr(obj, "b"),
        ],
    )
    def test_frozen_instance_is_immutable(
        self,
        new_frozen_instance: FrozenClass,
        obj_mutator: typing.Callable[[FrozenClass], None],
    ) -> None:
        with pytest.raises(
            frozen.FrozenObjectError,
            match=f"Object {new_frozen_instance!r} is frozen."
        ):
            obj_mutator(new_frozen_instance)


class TestThawable:
    def test_invalid_frozen_flag(self) -> None:
        frozen_flag = object
        with pytest.raises(
            ValueError,
            match=(
                f"__frozen__ expected a boolean value, "
                f"but {type(frozen_flag)}/{frozen_flag} received."
            ),
        ):
            class InvalidFrozenFlag(frozen.Thawable):
                __frozen__ = frozen_flag

    def test_invalid_thawed_attrs(self) -> None:
        thawed_attrs = []
        with pytest.raises(
            ValueError,
            match=re.escape(
                f"__thawed_attrs__ expected a set value, "
                f"but {type(thawed_attrs)}/{thawed_attrs} received."
            ),
        ):
            class InvalidThawedAttrs(frozen.Thawable):
                __thawed_attrs__ = thawed_attrs

    def test_thawable_instance_is_frozen_by_default(
        self, new_thawable_instance: ThawableClass,
    ) -> None:
        with pytest.raises(
            frozen.FrozenObjectError,
            match=f"Object {new_thawable_instance!r} is frozen.",
        ):
            new_thawable_instance.abc = 123

    def test___init___on_thawable_instance(
        self, new_thawable_instance: ThawableClass,
    ) -> None:
        assert new_thawable_instance.thawable_attr == 123

    def test_merge_thawed_attrs_on_thawable_instance(self) -> None:
        class _ThawableClass(frozen.Thawable):
            __thawed_attrs__ = {"change_value"}
            def __init__(self) -> None:
                self.value = 123
            def change_value(self) -> None:
                self.value = 321
            def unable_to_change_value(self) -> None:
                self.value = 321123

        obj = _ThawableClass()

        assert obj.value == 123
        obj.change_value()
        assert obj.value == 321

        with pytest.raises(
            frozen.FrozenObjectError,
            match=f"Object {obj!r} is frozen.",
        ):
            obj.unable_to_change_value()

    def test_frozen_flag_override_on_thawable_instance(self) -> None:
        class _ThawableClass(frozen.Thawable):
            __frozen__ = False
            def __init__(self) -> None:
                self.value = 123

        obj = _ThawableClass()

        assert obj.value == 123
        obj.value = 321
        assert obj.value == 321

    @pytest.mark.parametrize(
        "cls_mutator",
        [
            lambda cls: operator.setitem(cls, "a", "b"),
            lambda cls: setattr(cls, "c", "d"),
            lambda cls: operator.delitem(cls, "a"),
            lambda cls: delattr(cls, "b"),
        ],
    )
    def test_if_thawable_class_is_immutable(
        self,
        cls_mutator: typing.Callable[[typing.Type[typing.Any]], None],
    ) -> None:
        class _ThawableClass(frozen.Thawable):
            pass

        with pytest.raises(
            frozen.FrozenObjectError,
            match=f"Object {_ThawableClass!r} is frozen."
        ):
            cls_mutator(_ThawableClass)

    @pytest.mark.parametrize(
        "obj_mutator",
        [
            lambda obj: operator.setitem(obj, "a", "b"),
            lambda obj: setattr(obj, "c", "d"),
            lambda obj: operator.delitem(obj, "a"),
            lambda obj: delattr(obj, "b"),
        ],
    )
    def test_if_thawable_instance_is_immutable(
        self,
        new_thawable_instance: ThawableClass,
        obj_mutator: typing.Callable[[ThawableClass], None],
    ) -> None:
        with pytest.raises(
            frozen.FrozenObjectError,
            match=f"Object {new_thawable_instance!r} is frozen."
        ):
            obj_mutator(new_thawable_instance)

    def test_runtime_freeze_on_thawable_class(self) -> None:
        class _ThawableClass(frozen.Thawable):
            __frozen__ = False

            def __init__(self) -> None:
                self.value = 123

        class _ThawableSubclass(_ThawableClass):
            # The frozen parameter is not inherited
            __frozen__ = False

        obj = _ThawableClass()
        obj2 = _ThawableClass()
        subobj = _ThawableSubclass()

        assert obj.value == 123
        obj.value = 321
        assert obj.value == 321

        _ThawableClass.freeze()

        # Does not affect subclasses
        assert subobj.value == 123
        subobj.value = 321
        assert subobj.value == 321

        with pytest.raises(frozen.FrozenObjectError):
            obj.value = 111
        # But affect all of instances
        with pytest.raises(frozen.FrozenObjectError):
            obj2.value = 222

        with pytest.raises(
            frozen.FrozenError,
            match=f"Class {_ThawableClass.__name__!r} is already frozen.",
        ):
            _ThawableClass.freeze()

        # And
        _ThawableClass.freeze(strict=False)

    def test_runtime_thaw_on_thawable_class(self) -> None:
        class _ThawableClass(frozen.Thawable):
            def __init__(self) -> None:
                self.value = 123
            def by_default_unable_to_change_value(self) -> None:
                self.value = 321

        class _ThawableSubclass(_ThawableClass):
            pass

        obj = _ThawableClass()
        subobj = _ThawableSubclass()

        with pytest.raises(frozen.FrozenObjectError):
            obj.by_default_unable_to_change_value()

        # Thaws full class
        _ThawableClass.thaw()

        assert obj.value == 123
        obj.by_default_unable_to_change_value()
        assert obj.value == 321

        # Does not affect subclasses
        with pytest.raises(frozen.FrozenObjectError):
            subobj.by_default_unable_to_change_value()

    def test_runtime_thaw_attrs_on_thawable_class(self) -> None:
        class _ThawableClass(frozen.Thawable):
            def __init__(self) -> None:
                self.value = 123
            def by_default_unable_to_change_value(self) -> None:
                self.value = 321
            def foo(self) -> None:
                self.value = 111

        class _ThawableSubclass(_ThawableClass):
            pass

        obj = _ThawableClass()
        subobj = _ThawableSubclass()

        with pytest.raises(frozen.FrozenObjectError):
            obj.by_default_unable_to_change_value()

        _ThawableClass.thaw("by_default_unable_to_change_value")

        assert obj.value == 123
        obj.by_default_unable_to_change_value()
        assert obj.value == 321

        # Does not affect to other methods
        with pytest.raises(frozen.FrozenObjectError):
            obj.foo()

        _ThawableClass.thaw(
            {
                "by_default_unable_to_change_value",
                "foo",
            },
        )
        assert obj.value == 321
        obj.foo()
        assert obj.value == 111

        # Does not affect subclasses
        with pytest.raises(frozen.FrozenObjectError):
            subobj.foo()
        with pytest.raises(frozen.FrozenObjectError):
            subobj.by_default_unable_to_change_value()

        undefined_attr = "asfb"
        with pytest.raises(
            AttributeError,
            match=(
                f"Cannot thaw a non-existent "
                f"attribute {undefined_attr!r} in "
                f"cls {_ThawableClass.__name__!r}."
            ),
        ):
            _ThawableClass.thaw("asfb")

        # And
        _ThawableClass.thaw("asfb", ensure_attrs=False)

    def test_thawable_object_is_frozen(self) -> None:
        class _ThawableClass(frozen.Thawable):
            pass

        assert _ThawableClass.__frozen__
        assert _ThawableClass.is_frozen()
