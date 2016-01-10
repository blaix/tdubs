from querylist import QueryList


class Double(object):
    """A test double.

    >>> double = Double('my_double')

    Any interaction with it by default will return another double.

    >>> double.some_attribute
    Double(name='some_attribute')
    >>> double['some_key']
    Double(name='some_key')
    >>> double()
    Double(name='')

    You can define explicit attributes.

    >>> double.some_attribute = 'some value'
    >>> double.some_attribute
    'some value'

    >>> double = Double('my_double', predefined_attribute='predefined value')
    >>> double.predefined_attribute
    'predefined value'

    It can act like a dictionary.

    >>> double['some_key'] = 'some dict value'
    >>> double['some_key']
    'some dict value'

    >>> double['another_key'].foo = 'foo'
    >>> double['another_key'].foo
    'foo'

    You can stub direct calls.

    >>> calling(double).returns('some return value')
    >>> double()
    'some return value'

    You can stub method calls.

    >>> calling(double.some_method).returns('some method result')
    >>> double.some_method()
    'some method result'

    You can stub calls with specific arguments.

    >>> calling(double).passing('some argument').returns('specific value')
    >>> double('some argument')
    'specific value'

    When you do, the original stubs are retained.

    >>> double()
    'some return value'

    """
    def __init__(self, _name=None, **kwargs):
        self._name = _name or ''
        self._items = {}
        self._calls = QueryList(wrap=False)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return "Double(name='%s')" % self._name

    def __getattr__(self, name):
        attribute = Double(name)
        setattr(self, name, attribute)
        return attribute

    def __getitem__(self, key):
        self._items.setdefault(key, Double(key))
        return self._items[key]

    def __setitem__(self, key, value):
        self._items[key] = value

    def __call__(self, *args, **kwargs):
        try:
            return self._calls.get(args=args, kwargs=kwargs).return_value
        except QueryList.NotFound:
            return Double('')

    def _stub_call(self):
        """Stub a call to this double. Returns the Call object.

        This method is private to avoid conflicts with the object being
        replaced in tests. It is accessible via the public api as:

            calling(double)

        """
        call = Call()
        self._calls.insert(0, call)
        return call


calling = Double._stub_call


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
        self.return_value = None
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return '<Call args=%s kwargs=%s>' % (self.args, self.kwargs)

    def __eq__(self, other):
        return (self.args == other.args) and (self.kwargs == other.kwargs)

    def passing(self, *args, **kwargs):
        """Assign expected call args/kwargs to this call.

        Returns self for the common case of chaining a call to returns().

        """
        self.args = args
        self.kwargs = kwargs
        return self

    def returns(self, value):
        """Assign a specific return value to this call."""
        self.return_value = value
