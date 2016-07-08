"""Example test from the README.

Make sure any changes here are also made there, and vice versa. Ideally we
could just include this file in README.rst, but the include directive is not
supported on github: https://github.com/github/markup/issues/172

More ellaborate tests are in doctests.

"""
from __future__ import print_function
from unittest import TestCase

from tdubs import Stub, Spy, calling, verify


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

        # use spies to verify commands:
        self.printer = Spy()

        self.greeter = Greeter(prompter, self.printer)

    def test_prints_greeting_to_full_name(self):
        self.greeter.greet('Greetings')
        verify(self.printer).called_with('Greetings, Justin Blake!')
