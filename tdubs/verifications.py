from tdubs.doubles import Call, calls


class VerificationError(Exception):
    """Exception raised when verification of a call fails.

    See `Verification` for details or `README.rst` for examples.

    """
    pass


class Verification(object):
    """Verification objects are used to verify calls.

    See `README.rst` for details.

    """
    def __init__(self, spy):
        """Initialize with a spy.

        >>> from tdubs import Spy
        >>> spy = Spy('my spy')
        >>> Verification(spy)
        <Verification spy=<Spy name='my spy' ...>>

        It is also available as `verify` to make tests read better.

        >>> verify(spy)
        <Verification spy=<Spy name='my spy' ...>>

        """
        self.spy = spy

    def __repr__(self):
        """Represent a verification by the spy it's wrapping."""
        return '<Verification spy=%s>' % self.spy

    def called(self):
        """Return True if the spy was called.

        Otherwise raise VerificationError.

        """
        if calls(self.spy):
            return True
        raise VerificationError(
            "expected %s to be called, but it wasn't" % self.spy)

    def called_with(self, *args, **kwargs):
        """Return True if the spy was called with the specified args/kwargs.

        Otherwise raise VerificationError.

        """
        expected_call = Call(*args, **kwargs)
        if expected_call in calls(self.spy):
            return True
        raise VerificationError(
            "expected %s to be called with %s, but it wasn't" % (
                self.spy, expected_call.formatted_args))

    def not_called(self):
        """Return True if the spy was not called.

        Otherwise raise VerificationError.

        """
        if calls(self.spy):
            raise VerificationError(
                'expected %s to not be called, but it was' % self.spy)
        return True

    def not_called_with(self, *args, **kwargs):
        """Return True if spy was not called with the specified args/kwargs.

        Otherwise raise VerificationError.

        """
        call = Call(*args, **kwargs)
        if call in calls(self.spy):
            raise VerificationError(
                'expected %s to not be called with %s, but it was' % (
                    self.spy, call.formatted_args))
        return True

verify = Verification
