"""Example test from the README."""
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
