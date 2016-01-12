"""A test double library.

>>> my_stub = Stub('my_stub')

All attribute and key lookups on a stub will return another stub.

>>> my_stub.some_attribute
<Stub name='some_attribute' ...>
>>> my_stub['some_key']
<Stub name='some_key' ...>

You can define explicit attributes.

>>> my_stub.some_attribute = 'some value'
>>> my_stub.some_attribute
'some value'

>>> my_stub = Stub('my_stub', predefined_attribute='predefined value')
>>> my_stub.predefined_attribute
'predefined value'

It can act like a dictionary.

>>> my_stub['some_key'] = 'some dict value'
>>> my_stub['some_key']
'some dict value'

>>> my_stub['another_key'].foo = 'foo'
>>> my_stub['another_key'].foo
'foo'

You can stub direct calls.

>>> my_stub()
Traceback (most recent call last):
    ...
TypeError: <Stub name='my_stub' ...> is not callable

>>> calling(my_stub).returns('some return value')
>>> my_stub()
'some return value'

You can stub method calls.

>>> calling(my_stub.some_method).returns('some method result')
>>> my_stub.some_method()
'some method result'

You can stub calls with specific arguments.

>>> calling(my_stub).passing('some argument').returns('specific value')
>>> my_stub('some argument')
'specific value'

When you do, the original stubs are retained.

>>> my_stub()
'some return value'

If you want to verify calls, use a mock.

>>> my_mock = Mock('my_mock')

``Mock`` extends ``Stub`` to be automatically callable without stubbing.
Any call to a mock will return a new mock.

>>> my_mock()
<Mock ...>
>>> my_mock('arg1', 'arg2', foo='bar')
<Mock ...>

All calls to a mock are recorded.

>>> calls(my_mock)
[<Call args=() kwargs={}>, <Call args=('arg1', 'arg2') kwargs={'foo': 'bar'}>]

You can verify specific calls in your tests.

>>> verify(my_mock).called()
True
>>> verify(my_mock).called_with('arg1', 'arg2', foo='bar')
True
>>> verify(my_mock).called_with('foo')
Traceback (most recent call last):
    ...
tdubs.VerificationError: expected <Mock ...> to be called with ('foo'), ...
>>> new_mock = Mock('new_mock')
>>> verify(new_mock).called()
Traceback (most recent call last):
    ...
tdubs.VerificationError: expected <Mock ...> to be called, but it wasn't

>>> mock = Mock()
>>> verify(mock).not_called()
True
>>> mock()
<Mock ...>
>>> verify(mock).not_called()
Traceback (most recent call last):
    ...
tdubs.VerificationError: expected <Mock ...> to not be called, but it was

>>> verify(mock).not_called_with('foo')
True
>>> mock('foo')
<Mock ...>
>>> verify(mock).not_called_with('foo')
Traceback (most recent call last):
    ...
tdubs.VerificationError: expected <Mock ...> to not be called with (...), ...

"""


class Stub(object):
    def __init__(self, _name=None, **kwargs):
        self._name = _name or ''
        self._items = {}
        self._stubbed_calls = []
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "<%s name='%s' id='%s'>" % (
            self.classname, self._name, id(self))

    @property
    def classname(self):
        return type(self).__name__

    def __getattr__(self, name):
        attribute = type(self)(name)
        setattr(self, name, attribute)
        return attribute

    def __getitem__(self, key):
        self._items.setdefault(key, type(self)(key))
        return self._items[key]

    def __setitem__(self, key, value):
        self._items[key] = value

    def __call__(self, *args, **kwargs):
        actual_call = Call(*args, **kwargs)
        stubbed_call = next(
            (c for c in self._stubbed_calls if c == actual_call), None)
        return self._handle_call(actual_call, stubbed_call)

    def _handle_call(self, actual_call, stubbed_call):
        if not stubbed_call:
            raise TypeError('%s is not callable' % self)
        return stubbed_call.return_value

    def _stub_call(self):
        """Stub a call to this stub. Returns the Call object.

        This method is private to avoid conflicts with the object being
        replaced in tests. It is accessible via the public api as:

            calling(stub)

        """
        call = Call()
        self._stubbed_calls.insert(0, call)
        return call


calling = Stub._stub_call


class Mock(Stub):
    def __init__(self, *args, **kwargs):
        super(Mock, self).__init__(*args, **kwargs)
        self._actual_calls = []

    def _handle_call(self, actual_call, stubbed_call):
        self._actual_calls.append(actual_call)
        use_call = stubbed_call or actual_call
        return use_call.return_value

    def _get_calls(self):
        """Return list of call objects for every call made to the mock.

        This method is private to avoid conflicts with the object being
        replaced in tests. It is accessible via the public api as:

            calls(mock)

        """
        return self._actual_calls


calls = Mock._get_calls


class Call(object):
    """A representation of a function call.

    >>> call = Call()
    >>> call.args
    ()
    >>> call.kwargs
    {}

    >>> call.passing('foo', 'bar', baz='baz')
    <Call args=('foo', 'bar') kwargs={'baz': 'baz'}>
    >>> call.args
    ('foo', 'bar')
    >>> call.kwargs
    {'baz': 'baz'}

    >>> call.returns('value')
    >>> call.return_value
    'value'

    >>> call = Call('foo', bar='bar')
    >>> call == Call('asdf', bar='bar')
    False
    >>> call == Call('foo', bar='asdf')
    False
    >>> call == Call('foo', bar='bar')
    True

    """
    def __init__(self, *args, **kwargs):
        self.return_value = Mock()
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return '<Call args=%s kwargs=%s>' % (self.args, self.kwargs)

    def __eq__(self, other):
        return (self.args == other.args) and (self.kwargs == other.kwargs)

    @property
    def formatted_args(self):
        """Format call arguments as a string.

        >>> call = Call('arg1', 'arg2', kwarg='kwarg')
        >>> call.formatted_args
        "('arg1', 'arg2', kwarg='kwarg')"

        """
        arg_reprs = list(map(repr, self.args))
        kwarg_reprs = ['%s=%s' % (k, repr(v)) for k, v in self.kwargs.items()]
        return '(%s)' % ', '.join(arg_reprs + kwarg_reprs)

    def passing(self, *args, **kwargs):
        """Assign expected call args/kwargs to this call.

        Returns self for the common case of chaining a call to returns().

        >>> Call().passing('foo', bar='baz')
        <Call args=('foo',) kwargs={'bar': 'baz'}>

        """
        self.args = args
        self.kwargs = kwargs
        return self

    def returns(self, value):
        """Assign a specific return value to this call.

        >>> call = Call()
        >>> call.return_value
        <Mock ...>
        >>> call.returns('foo')
        >>> call.return_value
        'foo'

        """
        self.return_value = value


class Verification(object):
    def __init__(self, mock):
        self.mock = mock

    def called(self):
        """Return True if the mock was called.

        Otherwise raise VerificationError.

        """
        if calls(self.mock):
            return True
        raise VerificationError(
            "expected %s to be called, but it wasn't" % self.mock)

    def called_with(self, *args, **kwargs):
        """Return True if the mock was called with the specified args/kwargs.

        Otherwise raise VerificationError.

        """
        expected_call = Call(*args, **kwargs)
        if expected_call in calls(self.mock):
            return True
        raise VerificationError(
            "expected %s to be called with %s, but it wasn't" % (
                self.mock, expected_call.formatted_args))

    def not_called(self):
        """Return True if the mock was not called.

        Otherwise raise VerificationError.

        """
        if calls(self.mock):
            raise VerificationError(
                'expected %s to not be called, but it was' % self.mock)
        return True

    def not_called_with(self, *args, **kwargs):
        """Return True if mock was not called with the specified args/kwargs.

        Otherwise raise VerificationError.

        """
        call = Call(*args, **kwargs)
        if call in calls(self.mock):
            raise VerificationError(
                'expected %s to not be called with %s, but it was' % (
                    self.mock, call.formatted_args))
        return True

verify = Verification


class VerificationError(Exception):
    pass
