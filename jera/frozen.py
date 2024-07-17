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
"""
A module implementing the concept of class immutability.
By default, it is divided into two approaches: one allows the
use of immutability toggles or thawing specific methods, while
the second approach makes the object completely immutable.
"""
from __future__ import annotations

__all__: typing.Sequcence[str] = (
    "FrozenMeta",
    "ThawableMeta",
    "Frozen",
    "Thawable",
    "FrozenObjectError",
    "FROZEN_FLAG",
    "THAWED_ATTRS",
    "THAWED_DEFAULTS",
)

import typing
import sys

FROZEN_FLAG: typing.Final[str] = sys.intern("__frozen__")
"""
A constant that defines the attribute name serving as a flag 
indicating whether the object is currently frozen.

Note that if the object is frozen, it will not be permissible 
to modify it at either the class level or the instance level.

You can override methods or places where the class may be 
modified in the `__thawed_attrs__` attribute (see `THAWED_ATTRS`).
"""

THAWED_ATTRS: typing.Final[str] = sys.intern("__thawed_attrs__")
"""
A constant defining the name for a set containing method names 
or other places where the object is available for modification.

See `THAWED_DEFAULTS` for the default list of all methods where 
changes to the class or its instances occur.
"""

THAWED_DEFAULTS: typing.Final[typing.AbstractSet[str]] = {
    "__frozen_setattr__",
    "__frozen_delattr__",
    # Type level
    "__new__",
    "thaw",
    "freeze",
    # Instance level
    "__init__",
}
"""
Attributes or names of places, such as module name, where the 
object can be modified. By default, the location of the call is 
determined by calling `sys._getframe().f_back.f_code.co_name`.
"""


def __frozen_setattr__(
    ref: typing.Any,
    key: typing.Any,
    value: typing.Any,
) -> None:
    if (
        ref.__frozen__
        and sys._getframe().f_back.f_code.co_name
        not in getattr(ref, THAWED_ATTRS, ())
    ):
        raise FrozenObjectError(ref)

    try:
        if hasattr(ref, "__dict__"):
            ref.__dict__[key] = value
            return

        object.__setattr__(ref, key, value)

    # 1. Can't apply this __setattr__ to <Metaclass> object.
    # 2. At the metaclass level, __dict__ is of type
    #    mappingproxy and cannot be modified, which can also
    #    lead to a TypeError.
    except TypeError:
        # This happens when changes to the object occur at the
        # class level, and accordingly, the dunder methods of
        # the metaclass are called. We cannot apply
        # `object.__dunder_method__` to the metaclass, so we
        # refer to `type`.
        type.__setattr__(ref, key, value)


def __frozen_delattr__(ref: typing.Any, item: typing.Any) -> None:
    if (
        ref.__frozen__
        and sys._getframe().f_back.f_code.co_name
        not in getattr(ref, THAWED_ATTRS, ())
    ):
        raise FrozenObjectError(ref)

    try:
        object.__delattr__(ref, item)

    # Can't apply this __delattr__ to <Metaclass> object
    except TypeError:
        # This happens when changes to the object occur at the
        # class level, and accordingly, the dunder methods of
        # the metaclass are called. We cannot apply
        # `object.__dunder_method__` to the metaclass, so we
        # refer to `type`.
        type.__delattr__(ref, item)


def _freeze_cls_attrs(
    attrs: typing.Dict[str, typing.Any], /,
) -> typing.Dict[str, typing.Any]:
    attrs["__setattr__"] = attrs["__setitem__"] = __frozen_setattr__
    attrs["__delattr__"] = attrs["__delitem__"] = __frozen_delattr__
    return attrs


class FrozenError(Exception):
    """The base class for all exceptions related to this module."""
    pass


class FrozenObjectError(FrozenError):
    """
    An exception that is raised if an attempt is made to
    modify a frozen object.

    Parameters
    ----------
    obj : typing.Any
        A frozen object that was attempted to be modified.
    """

    def __init__(self, obj: typing.Any) -> None:
        super().__init__(f"Object {obj!r} is frozen.")
        self._obj = obj

    @property
    def obj(self) -> typing.Any:
        """A frozen object that was attempted to be modified."""
        return self._obj


class FrozenMeta(type):
    __frozen__: bool

    # We remove the ability to modify the object at the class level.
    # These dunder methods are triggered when attempting to add or
    # remove an attribute from the class.
    #
    # Note that changing the object at the class level will result
    # in changes across all its instances.
    #
    # All thawed points where object modification can occur are
    # listed in the `THAWED_DEFAULTS` constant.
    __setattr__ = __setitem__ = __frozen_setattr__
    __delattr__ = __delitem__ = __frozen_delattr__

    def __new__(
        mcs: typing.Type[ThawableMeta],
        name: str,
        bases: typing.Tuple[typing.Type[typing.Any], ...],
        attrs: typing.Dict[str, typing.Any],
    ) -> typing.Any:
        frozen = attrs.pop(FROZEN_FLAG, True)
        if not isinstance(frozen, bool):
            raise ValueError(
                f"__frozen__ expected a boolean value, "
                f"but {type(frozen)}/{frozen} received."
            )

        if not frozen:
            raise ValueError(
                "__frozen__ cannot be builtins.False in "
                "a subclass of FrozenMeta."
            )

        frozen = super().__new__(
            mcs,
            name,
            bases,
            _freeze_cls_attrs(attrs),
        )
        return frozen


class ThawableMeta(type):
    __frozen__: bool
    __thawed_attrs__: typing.MutableSet[str]

    # We remove the ability to modify the object at the class level.
    # These dunder methods are triggered when attempting to add or
    # remove an attribute from the class.
    #
    # Note that changing the object at the class level will result
    # in changes across all its instances.
    #
    # All thawed points where object modification can occur are
    # listed in the `THAWED_DEFAULTS` constant.
    __setattr__ = __setitem__ = __frozen_setattr__
    __delattr__ = __delitem__ = __frozen_delattr__

    def __new__(
        mcs: typing.Type[ThawableMeta],
        name: str,
        bases: typing.Tuple[typing.Type[typing.Any], ...],
        attrs: typing.Dict[str, typing.Any],
    ) -> typing.Any:
        frozen = attrs.pop(FROZEN_FLAG, True)
        if not isinstance(frozen, bool):
            raise ValueError(
                f"__frozen__ expected a boolean value, "
                f"but {type(frozen)}/{frozen} received."
            )

        thawed = attrs.pop(THAWED_ATTRS, set())
        if not isinstance(thawed, set):
            raise ValueError(
                f"__thawed_attrs__ expected a set value, "
                f"but {type(thawed)}/{thawed} received."
            )

        thawed |= THAWED_DEFAULTS

        attrs[THAWED_ATTRS] = thawed
        attrs[FROZEN_FLAG] = frozen

        thawable = super().__new__(
            mcs,
            name,
            bases,
            _freeze_cls_attrs(attrs),
        )
        return thawable

    def freeze(
        cls,
        *,
        strict: bool = True,
    ) -> None:
        """
        Freezes the current state of the class, including
        the class itself.

        Parameters
        ----------
        strict : bool
            If set to `builtins.True`, an attempt to freeze
            an already frozen class will raise a FrozenError.
            By default, it is set to `builtins.True`.

        Raises
        ------
        FrozenError
            Raised when attempting to freeze an already frozen
            class, given that `strict` is set to `builtins.True`.
        """
        if strict and cls.is_frozen():
            raise FrozenError(
                f"Class {cls.__name__!r} is already frozen."
            ) from None

        cls.__frozen__ = True

    def thaw(
        cls,
        attrs: typing.Optional[
            typing.Union[str, typing.AbstractSet[str]]
        ] = None,
        *,
        ensure_attrs: bool = True,
    ) -> None:
        """
        Unfreezes the current state of the class or specific
        attributes.

        Parameters
        ----------
        attrs : Optional[Union[str, AbstractSet[str]]]
            It can be a single attribute or multiple attributes.
            If `builtins.None` is received, the entire class will
            be unfrozen.
            By default, it is set to `builtins.None`.
        ensure_attrs : bool
            If one or more attributes are passed in `attrs`, and
            `ensure_attrs` is set to `builtins.True`, the presence
            of the attribute(s) in the class directory will be
            checked before unfreezing. If an attribute is
            missing, an exception will be raised.
            By default, it is set to `builtins.True`.

        Raises
        ------
        Raised if `ensure_attrs` is `builtins.True` and one of
        the attributes passed in `attrs` is not found in the
        class directory.
        """
        if attrs is None:
            cls.__frozen__ = False
            return

        if not isinstance(attrs, typing.AbstractSet):
            attrs = {attrs}

        if ensure_attrs:
            cls_dir = dir(cls)
            for attr in attrs:
                if attr not in cls_dir:
                    raise AttributeError(
                        f"Cannot thaw a non-existent "
                        f"attribute {attr!r} in "
                        f"cls {cls.__name__!r}."
                    ) from None

        cls.__thawed_attrs__ |= attrs

    def is_frozen(cls) -> bool:
        """
        Returns a boolean value indicating whether the current
        state of the class is frozen or not.
        """
        frozen = typing.cast(
            typing.Optional[bool],
            getattr(cls, FROZEN_FLAG, None),
        )
        if frozen is None:
            raise AttributeError(
                f"Missing {FROZEN_FLAG!r} in "
                f"{cls.__name__!r} class."
            ) from None

        return cls.__frozen__


class Frozen(metaclass=FrozenMeta):
    """
    A class that freezes the methods `__setattr__`, `__setitem__`,
    `__delattr__`, and `__delitem__` for the current instance of the
    class and the class itself. However, the class can be modified
    in `__init__` for initial initialization.

    Note that unlike `Thawable`, this class does not provide the
    ability to unfreeze the state of the class or specific attributes.
    """
    pass


class Thawable(metaclass=ThawableMeta):
    """
    A class that freezes the methods `__setattr__`, `__setitem__`,
    `__delattr__`, and `__delitem__` for the current instance of the
    class and the class itself. However, the class can be modified
    in `__init__` for initial initialization.

    __frozen__ : bool
    ----------
    A flag to determine the state of the current instance, whether
    it is frozen or not.
    By default, it is set to `builtins.True`.

    __thawed_attrs__ : set
    ----------------
    A parameter that defines the attributes that will be unfrozen
    and therefore can change the state of the current instance of
    the class.

    This parameter is implicit and can create many unexpected
    problems, so use it with caution and only in very exotic cases.
    """
    pass
