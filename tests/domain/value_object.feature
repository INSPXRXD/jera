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
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.Feature: ValueObject
Feature: ValueObject
  """
  A value object is primarily an element of a model defined by its attributes and lacking
  individual existence. These objects are created in a program to represent those
  elements of a project that only need to be understood by what they are, not who they are.

  This domain pattern is characterized by the following properties:

  - A value object can represent a collection of other objects.
  - Value objects can reference entities.
  - Value objects are often passed as parameters in messages between objects. They are
    frequently temporary, created for a specific operation and then destroyed.
  - Value objects can be used as attributes of entities (and other values). For example,
    a person as a whole can be represented as an individual entity, but their name would be
    a value object.
  - The attributes that collectively form a value object should be a single conceptual
    whole (Whole Value Pattern).

  Methods within value objects
  -------
  A method within a value object should be designed as a "function without side effects."
  A function without side effects is an operation on an object that generates a result but
  does not modify its state. All methods of an immutable value object should be functions
  without side effects because they should not violate the immutability property.

  Special cases when mutability is allowed
  -------
  Immutability of objects significantly simplifies software implementation, ensuring safe
  concurrent use and reference passing. It also aligns with the idea of objects as values.
  If the value of an attribute changes, instead of modifying the existing value object,
  a new one is used. However, there are cases when, for performance reasons, it is better
  to allow modifications in value objects. The factors that usually support this are:

  - Frequent changes to the value object.
  - High cost of creating and destroying the object.
  - The danger of replacement instead of modification when grouping objects.
  - Insignificant concurrent use or a complete rejection of it to improve object grouping
    and for some other technical reasons.

  Are all attributes value objects?
  -------
  One should be somewhat cautious in situations where there are truly simple attributes
  that do not require special handling. Perhaps these are boolean types or numeric values
  that are indeed self-contained, do not require additional functional support, and are
  not associated with any other attributes of the same entity. Such simple attributes
  represent a "meaningful whole."
  """

  Scenario: Considering an immutable value object
    """Immutable value objects free us from responsibility."""
    Given an immutable value object
    When we attempt to change its state
    Then an exception is raised informing us that the object is immutable

  Scenario: Considering a mutable value object
    """In this case, the mutable object is completely free."""
    Given a mutable value object
    When we change its state
    Then the state of the value object is successfully updated without exceptions

  Scenario: Compatibility of value objects with third-party libraries
    """
    A value object is immutable from the moment of inheritance,
    some libraries using various methods (e.g., decorators),
    prepare value objects by changing the state of the class.

    In such cases, it is necessary to pre-unfreeze certain places where
    the value object will undergo changes. These could be
    function names or modules where the changes occur.
    """
    Given an immutable value object wrapped in a dataclass
    And we have pre-unfrozen the dataclass for changes in the value object
    When the process of preparing the value object by a third-party module occurs
    Then the class is successfully transformed without exceptions

  Scenario: Dynamic unfreezing and freezing of a value object
    """
    In exotic cases, there may be a need to dynamically unfreeze and
    freeze certain attributes or modules, which is considered in this scenario.
    """
    Given an immutable value object with a method that has side effects
    And the method is not pre-unfrozen for changes in the value object
    When we unfreeze the method with side effects and call it
    Then the state of the value object is successfully changed
