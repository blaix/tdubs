TDubs
=====

A test double library for python.

.. contents::
    :local:
    :backlinks: none

Example
-------

.. include:: example_test.py
    :code: python
    :start-line: 1

See ``tdubs.py`` for full usage.

Stubs vs. Mocks
---------------

You should use ``Stub`` when you are testing behavior that depends on the state
or return value of some other object. For example, the behavior of the
``Greeter`` above depends on the return value of ``prompter``, so I'm using a
stub.

Stubs are not callable by default. You must explicitly stub a return value if
you expect it to be called. This is to avoid false positives in your tests for
behavior that may depend on the truthiness of that call.

Mocks *are* callable by default, because they are designed to record calls for
verification after execution. You should use ``Mock`` when you only need to
verify that something was called.  For example, I need to verify whether or not
``printer`` was called with the correct string, so I'm using a mock.

You can think of it this way: use ``Stub`` for *queries*, and ``Mock`` for
*commands*.  If the separation isn't clear, spend some time thinking about your
design. Would it be better with distinct queries and commands? (If you really
need both, use ``Mock``, since it extends ``Stub``).

Further reading:

- `Mocks aren't Stubs <http://martinfowler.com/articles/mocksArentStubs.html>`_
- `The Little Mocker <https://blog.8thlight.com/uncle-bob/2014/05/14/TheLittleMocker.html>`_
- `Mock Roles, not Objects <http://www.jmock.org/oopsla2004.pdf>`_

Why?
----

Python 3 already has ``unittest.mock``, and there are several other third-party
test double packages, but none felt like the right fit for how I like to TDD.

This is what I wanted out of a test double library:

1. The ability to treat a double as a callable with return values specific to
   the arguments passed in. This is so I can treat stubs as pure stubs, without
   needing to verify I passed the right arguments to my query methods. You can
   see that in action in the example above.

2. The ability to verify calls after they are made, without setting up
   expectations first.  This is so my tests read like a story::

        # set up:
        my_mock = Mock()

        # execute:
        my_func(my_mock)

        # verify:
        verify(my_mock).called()

3. Test doubles with zero public attributes from the library. This is to avoid
   conflicts with the object being replaced in tests. For example:

   Since all attributes on a mock return a new mock, the following
   assertion  will always evaluate to True::
       
       >>> from unittest import mock
       >>> mock.Mock().asssert_called_with('foo')  # oops!
       <Mock ...>

   Notice the typo? If not, you may get a false positive in your test.

   tdubs avoids this by using a new object for verifications::
        
       >>> from tdubs import Mock, verify
       >>> verify(Mock()).callled_with('foo')  # oops!
       Traceback (most recent call last):
            ...
       AttributeError: 'Verification' object has no attribute 'callled_with'

   Notice the typo? If not, it doesn't matter. Python noticed!

I also like the distinction between stubs and mocks (see `Stubs vs.  Mocks`_),
but it's not one of the reasons I originally decided to write tdubs.

Installation
------------

Coming soon. For now, just download ``tdubs.py``.

Development
-----------

Clone the project.

Install dependencies::

    pip install -r requirements.txt

Run the tests::

    nosetests --with-doctest --doctest-options=+ELLIPSIS --doctest-extension=rst

Lint and test the code automatically when changes are made (see ``tube.py``)::

    stir
