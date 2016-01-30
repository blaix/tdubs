TDubs
=====

A test double library for python 3.

.. contents::
    :local:
    :backlinks: none

Example
-------

.. code:: python

    from unittest import TestCase

    from tdubs import Stub, Mock, calling, verify


    # The thing I want to test:
    class Greeter(object):

        # tdubs works best with code that has injectable dependencies:
        def __init__(self, prompter=None, printer=None):
            self.prompter = prompter or input
            self.printer = printer or print

        def greet(self, greeting):
            fname = self.prompter('First name:')
            lname = self.prompter('Last name:')
            self.printer('%s, %s %s!' % (greeting, fname, lname))


    class TestGreeter(TestCase):
        def setUp(self):
            # use stubs to provide canned responses to queries:
            prompter = Stub()
            calling(prompter).passing('First name:').returns('Justin')
            calling(prompter).passing('Last name:').returns('Blake')

            # use mocks to verify commands:
            self.printer = Mock()

            self.greeter = Greeter(prompter, self.printer)

        def test_prints_greeting_to_full_name(self):
            self.greeter.greet('Greetings')
            verify(self.printer).called_with('Greetings, Justin Blake!')

Usage
-----

Creating stubs
..............

.. code::

    >>> from tdubs import Stub
    >>> my_stub = Stub('my_stub')

Attributes
..........

All attribute and key lookups on a stub will return another stub::

    >>> my_stub.some_attribute
    <Stub name='some_attribute' ...>

You can define explicit attributes::

    >>> my_stub.some_attribute = 'some value'
    >>> my_stub.some_attribute
    'some value'

    >>> my_stub = Stub('my_stub', predefined_attribute='predefined value')
    >>> my_stub.predefined_attribute
    'predefined value'

Dictionaries
............

Key lookups work the same way as attribute lookups::

    >>> my_stub['some_key']
    <Stub name='some_key' ...>
    >>> my_stub['some_key'] = 'some dict value'
    >>> my_stub['some_key']
    'some dict value'

    >>> my_stub['another_key'].foo = 'foo'
    >>> my_stub['another_key'].foo
    'foo'

Callables
.........

You must explictly make your stub callable. This is to avoid false positives
in tests for logic that may depend on the truthyness of a return value.

.. code::

    >>> my_stub()
    Traceback (most recent call last):
        ...
    TypeError: <Stub name='my_stub' ...> is not callable ...

    >>> from tdubs import calling
    >>> calling(my_stub).returns('some return value')
    >>> my_stub()
    'some return value'

Since attribute lookups return a stub by default, you can treat your stub like
an object with callable methods::

    >>> calling(my_stub.some_method).returns('some method result')
    >>> my_stub.some_method()
    'some method result'

You can stub calls with specific arguments::

    >>> calling(my_stub).passing('some argument').returns('specific value')
    >>> my_stub('some argument')
    'specific value'

When you do, the original stubs are retained::

    >>> my_stub()
    'some return value'

Mocks
.....

Mocks have all the functionality of stubs, but they are callable by default,
and will record calls for verification. So if you need to verify calls, use a
mock (see `Stubs vs. Mocks`_ for more details).

.. code::

    >>> from tdubs import Mock
    >>> my_mock = Mock('my_mock')

Any call to a mock will return a new mock::

    >>> my_mock()
    <Mock ...>
    >>> my_mock('arg1', 'arg2', foo='bar')
    <Mock ...>

All calls to a mock are recorded::

    >>> from tdubs import calls
    >>> calls(my_mock)
    [<Call args=() kwargs={}>, <Call args=('arg1', 'arg2') kwargs={'foo': 'bar'}>]

You can verify that something was called::

    >>> from tdubs import verify
    >>> verify(my_mock).called()
    True

    >>> new_mock = Mock('new_mock')
    >>> verify(new_mock).called()
    Traceback (most recent call last):
        ...
    tdubs.VerificationError: expected <Mock ...> to be called, but it wasn't

You can verify that it was called with specific arguments::

    >>> verify(my_mock).called_with('arg1', 'arg2', foo='bar')
    True
    >>> verify(my_mock).called_with('foo')
    Traceback (most recent call last):
        ...
    tdubs.VerificationError: expected <Mock ...> to be called with ('foo'), ...

You can also verify that it was *not* called::

    >>> verify(new_mock).not_called()
    True
    >>> new_mock()
    <Mock ...>
    >>> verify(new_mock).not_called()
    Traceback (most recent call last):
        ...
    tdubs.VerificationError: expected <Mock ...> to not be called, but it was

Or that it was not called with specific arguments::

    >>> verify(new_mock).not_called_with('foo')
    True
    >>> new_mock('foo')
    <Mock ...>
    >>> verify(new_mock).not_called_with('foo')
    Traceback (most recent call last):
        ...
    tdubs.VerificationError: expected <Mock ...> to not be called with (...), ...

Stubs vs. Mocks
---------------

You should use ``Stub`` when you are testing behavior that depends on the state
or return value of some other object. For example, the behavior of the
``Greeter`` in the `Example`_ above depends on the return value of
``prompter``, so I'm using a stub.

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

I also like the distinction between stubs and mocks (see `Stubs vs. Mocks`_),
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
