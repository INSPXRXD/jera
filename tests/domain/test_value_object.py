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

import copy
import dataclasses
import typing

import pytest_bdd as ts  # technical specifications
from hamcrest import assert_that
from hamcrest import calling
from hamcrest import raises
from hamcrest import not_
from hamcrest import is_
from hamcrest import equal_to

from jera.domain import value_object
from jera import frozen


@ts.scenario("value_object.feature", "Considering an immutable value object")
def test_considering_an_immutable_value_object() -> None:
    pass


@ts.given(
    "an immutable value object",
    target_fixture="immutable_value_object",
)
def _() -> value_object.ValueObject:
    class ImmutableValueObject(value_object.ValueObject):
        pass

    vobj = ImmutableValueObject()
    return vobj


@ts.when("we attempt to change its state")
@ts.then("an exception is raised informing us that the object is immutable")
def _(immutable_value_object: value_object.ValueObject) -> None:
    def modify_immutable_value_object_state() -> None:
        immutable_value_object.awesome_attribute = "^_^"

    assert_that(
        calling(modify_immutable_value_object_state),
        raises(frozen.FrozenObjectError)
    )


@ts.scenario("value_object.feature", "Considering a mutable value object")
def test_considering_a_mutable_value_object() -> None:
    pass


@ts.given(
    "a mutable value object",
    target_fixture="mutable_value_object",
)
def _() -> value_object.ValueObject:
    class MutableValueObject(value_object.ValueObject):
        __frozen__: bool = False

    vobj = MutableValueObject()
    return vobj


@ts.when("we change its state")
@ts.then("the state of the value object is successfully updated without exceptions")
def _(mutable_value_object: value_object.ValueObject) -> None:
    def modify_mutable_value_object_state() -> None:
        mutable_value_object.awesome_attribute = "^_^"

    assert_that(
        calling(modify_mutable_value_object_state),
        not_(raises(frozen.FrozenObjectError))
    )


@ts.scenario("value_object.feature", "Compatibility of value objects with third-party libraries")
def test_compatibility_of_value_object_with_third_party_libraries() -> None:
    pass


@ts.given(
    "an immutable value object wrapped in a dataclass",
    target_fixture="wrapped_immutable_value_object",
)
@ts.given(
    "we have pre-unfrozen the dataclass for changes in the value object",
)
def _() -> value_object.ValueObject:
    @dataclasses.dataclass
    class WrappedImmutableValueObject(value_object.ValueObject):
        __thawed__: typing.ClassVar[typing.AbstractSet[str]] = {"dataclasses"}

    vobj = WrappedImmutableValueObject()
    return vobj


@ts.when("the process of preparing the value object by a third-party module occurs")
@ts.then("the class is successfully transformed without exceptions")
def _(wrapped_immutable_value_object: value_object.ValueObject) -> None:
    assert_that(
        dataclasses.is_dataclass(wrapped_immutable_value_object),
        is_(True),
    )


@ts.scenario("value_object.feature", "Dynamic unfreezing and freezing of a value object")
def test_dynamic_unfreezing_and_freezing_of_a_value_object() -> None:
    pass


@ts.given(
    "an immutable value object with a method that has side effects",
    target_fixture="immutable_value_object",
)
@ts.given(
    "the method is not pre-unfrozen for changes in the value object",
)
def _() -> value_object.ValueObject:
    class ImmutableValueObject(value_object.ValueObject):
        __thawed__: typing.ClassVar[typing.AbstractSet[str]] = {
            "state_modifying_method",
        }

        def __init__(self) -> None:
            self.awesome_attr = ":)"

        def state_modifying_method(self) -> None:
            self.awesome_attr = ":("

    vobj = ImmutableValueObject()
    return vobj


@ts.when("we unfreeze the method with side effects and call it")
@ts.then("the state of the value object is successfully changed")
def _(immutable_value_object: value_object.ValueObject) -> None:
    other_imm_vobj = copy.deepcopy(immutable_value_object)

    assert_that(
        calling(lambda: setattr(immutable_value_object, "abcdefg", 123)),
        raises(frozen.FrozenObjectError),
    )

    type(immutable_value_object).thaw("state_modifying_method")

    assert_that(
        immutable_value_object.awesome_attr,
        equal_to(":)"),
    )

    # Due to the structure of the pytest library, this check modifies
    # the state of a copy of the value object, which is tested in the
    # following block
    assert_that(
        calling(other_imm_vobj.state_modifying_method),
        not_(raises(frozen.FrozenObjectError)),
    )
    assert_that(
        other_imm_vobj.awesome_attr,
        equal_to(":("),
    )
