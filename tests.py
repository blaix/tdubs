"""Example test from the README.

TODO: how to keep these in sync?

More ellaborate tests are in doctests.

"""
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
