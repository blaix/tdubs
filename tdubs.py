class Stub(object):
    def __init__(self, _name=None, **kwargs):
        self._name = _name or ''
        self._dict_items = {}
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
        self._dict_items.setdefault(key, type(self)(key))
        return self._dict_items[key]

    def __setitem__(self, key, value):
        self._dict_items[key] = value

    def __call__(self, *args, **kwargs):
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
