"""Configuration for testtube.
Automatically run tests when files change by running: stir
See: https://github.com/thomasw/testtube
For flake8, don't forget to install:
* flake8-quotes
"""

from testtube.helpers import Flake8, Helper, Nosetests


class ScreenClearer(Helper):
    command = 'clear'

    def success(self, *args):
        pass


class Isort(Helper):
    command = 'isort'

    def get_args(self):
        return ['--check']


class UnitTests(Nosetests):
    """Run test cases in the tests/ directory."""

    def get_args(self, *args, **kwargs):
        return ['-x', '--with-doctest', '--doctest-options=+ELLIPSIS']


clear = ScreenClearer(all_files=True)
lint_style = Flake8(all_files=True)
unit_tests = UnitTests(all_files=True)

PATTERNS = (
    (r'.*\.py$', [clear]),
    (r'.*\.py$', [unit_tests], {'fail_fast': True}),
    (r'.*\.py$', [lint_style], {'fail_fast': True}),
)
