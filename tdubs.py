class Stub(object):
    """A test double that can stand in for another object in your test.

    Use this when the logic you are testing depends on the state or return
    value of a collaborator.

    See `README.rst` for details.

    """
    def __init__(self, _name=None, **kwargs):
        """Initialize a stub, optionally with a name and/or attributes.

        >>> Stub()
        <Stub name='' ...>

        >>> Stub('my stub')
        <Stub name='my stub' ...>

        >>> stub = Stub(foo='bar')
        >>> stub.foo
        'bar'

        >>> stub = Stub('my stub', foo='bar')
        >>> stub
        <Stub name='my stub' ...>
        >>> stub.foo
        'bar'

        """
        self._name = _name or ''
        self._dict_items = {}
        self._stubbed_calls = []
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        """Return representation of this test double.

        The name and object id are shown to make test failure output more
        helpful.

        >>> stub = Stub('my stub')
        >>> repr(stub)
        "<Stub name='my stub' id='...'>"

        """
        return "<%s name='%s' id='%s'>" % (
            self.classname, self._name, id(self))

    @property
    def classname(self):
        return type(self).__name__

    def __getattr__(self, name):
        """For unknown attributes: create, set, and return a new double.

        >>> stub = Stub()
        >>> stub.foo
        <Stub name='foo' ...>

        """
        attribute = type(self)(name)
        setattr(self, name, attribute)
        return attribute

    def __getitem__(self, key):
        """Provide dict behavior similar to attribute behavior.

        Assigned keys will return the assigned value. New keys will set and
        return a new double.

        >>> stub = Stub()
        >>> stub['foo'] = 'foo'
        >>> stub['foo']
        'foo'
        >>> stub['bar']
        <Stub name='bar' ...>

        """
        self._dict_items.setdefault(key, type(self)(key))
        return self._dict_items[key]

    def __setitem__(self, key, value):
        """Assign a specific value for this key."""
        self._dict_items[key] = value

    def __call__(self, *args, **kwargs):
        """Return stubbed value for this call.

        Raises TypeError if there is no stubbed value for this call.

        """
        actual_call = Call(*args, **kwargs)
        stubbed_call = next(
            (c for c in self._stubbed_calls if c == actual_call), None)
        return self._handle_call(actual_call, stubbed_call)

    def _handle_call(self, actual_call, stubbed_call):
        if not stubbed_call:
            raise TypeError('%s is not callable with %s' % (
                self, actual_call.formatted_args))
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
    """A test double that stands in for a delegate callable in your test.

    Provides all the behavior of Stub, but is callable by default, and records
    calls for verification.

    Use a Mock when you are testing behavior that includes delegating to some
    other callable.

    See `README.rst` for details.

    """
    def __init__(self, *args, **kwargs):
        """Initialize a new Mock. See `Stub.__init__` for details."""
        super(Mock, self).__init__(*args, **kwargs)
        self._actual_calls = []

    def _handle_call(self, actual_call, stubbed_call):
        """Extends Stub call handling behavior to be callable by default."""
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

    A call is identified by its args and kwargs.

    """
    def __init__(self, *args, **kwargs):
        """Initialize a call. Optionally with args and/or kwargs.

        >>> call = Call()
        >>> call.args
        ()
        >>> call.kwargs
        {}

        >>> call = Call('foo', bar='bar')
        >>> call.args
        ('foo',)
        >>> call.kwargs
        {'bar': 'bar'}

        """
        self._return_value = Mock()
        self.exception = None
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        """Represent a Call by its args and kwargs.

        >>> call = Call('foo', bar='bar')
        >>> repr(call)
        "<Call args=('foo',) kwargs={'bar': 'bar'}>"

        """
        return '<Call args=%s kwargs=%s>' % (self.args, self.kwargs)

    def __eq__(self, other):
        """Calls are equal if they have the same args and kwargs.

        This is what lets call verification work in tests. Call stubs and
        actual calls are saved as a `Call` with the given args and kwargs,
        and then verified by checking if they are equal with `==`.

        >>> Call() == Call()
        True

        >>> Call('foo') == Call()
        False

        >>> Call('foo') == Call('bar')
        False

        >>> Call('foo') == Call('foo', bar='bar')
        False

        >>> Call('foo', bar='bar') == Call('foo', bar='bar')
        True

        """
        return (self.args == other.args) and (self.kwargs == other.kwargs)

    @property
    def return_value(self):
        """Return assigned return_value, or raise exception if present."""
        if self.exception:
            raise self.exception
        return self._return_value

    @property
    def formatted_args(self):
        """Format call arguments as a string.

        This is used to make test failure messages more helpful by referring
        to calls using a string that matches how they were, or should have been
        called.

        >>> call = Call('arg1', 'arg2', kwarg='kwarg')
        >>> call.formatted_args
        "('arg1', 'arg2', kwarg='kwarg')"

        """
        arg_reprs = list(map(repr, self.args))
        kwarg_reprs = ['%s=%s' % (k, repr(v)) for k, v in self.kwargs.items()]
        return '(%s)' % ', '.join(arg_reprs + kwarg_reprs)

    def passing(self, *args, **kwargs):
        """Assign expected call args/kwargs to this call.

        Returns `self` for the common case of chaining a call to `Call.returns`

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
        self._return_value = value

    def raises(self, exception):
        """Assign an exception to this call.

        >>> call = Call()
        >>> call.raises(Exception('Blam!'))
        >>> call.exception
        Exception('Blam!',)

        Exceptions are raised when trying to access the return value:

        >>> call.return_value
        Traceback (most recent call last):
            ...
        Exception: Blam!

        """
        self.exception = exception


class Verification(object):
    """Verification objects are used to verify mocked calls.

    See `README.rst` for details.

    """
    def __init__(self, mock):
        """Initialize with a mock.

        >>> mock = Mock('my mock')
        >>> Verification(mock)
        <Verification mock=<Mock name='my mock' ...>>

        It is also available as `verify` to make tests read better.

        >>> verify(mock)
        <Verification mock=<Mock name='my mock' ...>>

        """
        self.mock = mock

    def __repr__(self):
        """Represent a verification by the mock it's wrapping."""
        return '<Verification mock=%s>' % self.mock

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
    """Exception raised when verification of a call fails.

    See `Verification` for details or `README.rst` for examples.

    """
    pass
