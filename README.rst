TDubs
=====

A test double library for python.

.. contents::
    :local:
    :backlinks: none

Example
-------

.. code:: python

    from unittest import TestCase

    from tdubs import Stub, Mock, calling, verify


    # typically over-simplified example:
    class ResourceCreator(object):
        def __init__(self, validator, repository):
            self.validator = validator
            self.repository = repository

        def __call__(self, data):
            if self.validator.is_valid(data):  # a query
                self.repository.insert(data)   # a command


    class TestResourceCreator(TestCase):
        def setUp(self):
            # stubs are great for providing canned responses to queries:
            validator = Stub()
            calling(validator.is_valid).passing('good data').returns(True)
            calling(validator.is_valid).passing('bad data').returns(False)

            # mocks are great for verfying commands:
            self.repository = Mock()

            self.create_resource = ResourceCreator(validator, self.repository)

        def test_inserts_valid_data(self):
            self.create_resource('good data')
            verify(self.repository.insert).called_with('good data')

        def test_does_not_insert_invalid_data(self):
            self.create_resource('bad data')
            verify(self.repository.insert).not_called()

See ``tdubs.py`` for full usage.

Stubs vs. Mocks
---------------

You should use ``Stub`` when you are testing behavior that depends on the state
or return value of some other object. For example, the behavior of the
``ResourceCreator`` above depends on the return value of
``validator.is_valid``, so I'm using a stub.

You should use ``Mock`` when you only need to verify that something was called.
For example, I need to verify if ``repository.insert`` was called with our
data, so I'm using a mock.

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
   conflicts with the object being replaced in tests. For example::

       Since all attributes on a mock return a new mock,
       this will always evaluate to True (notice the typos?):
       
       >>> from unittest import mock
       >>> mock.Mock().asssert_called_with('foo')  # oops!
       <Mock ...>

       Not possible with tdubs, since verifications happen on a new object:
        
       >>> from tdubs import Mock, verify
       >>> verify(Mock()).callled_with('foo')  # oops!
       Traceback (most recent call last):
            ...
       AttributeError: 'Verification' object has no attribute 'callled_with'

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
