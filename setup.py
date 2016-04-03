import multiprocessing  # noqa `python setup.py test` fix for python 2.6
from setuptools import setup
import sys

# We need the following dependenices so that setup.py's command nosetests will
# run correclty without manually installing all dev dependencies. Note that
# these requirements cannot be specified as setup's tests_require param
# because tests_require dependencies are not installed before attempting to
# execute nosetests. nosetests is necessary because python setup.py test
# will not capture doctests.
setup_requires = ['nose==1.3.7', 'coverage==4.0.3']

# mock is needed for doctests; it wasn't added to stdlib until python 3.3
if sys.version_info[:2] < (3, 3):
    setup_requires += ['mock==1.3.0']

# coverage doesn't support python 3.2. Coverage reporting will fail in 3.2
if sys.version_info[:2] == (3, 2):
    setup_requires.remove('coverage==4.0.3')

setup(
    name='tdubs',
    version='0.2.0',
    url='https://github.com/blaix/tdubs',
    author='Justin Blake',
    author_email='justin@blaix.com',
    description='A test double library',
    py_modules=['tdubs'],
    setup_requires=setup_requires,
    license='MIT (Expat)',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Testing',
    ],
    # The following allows the test command to find and execute unit tests
    # but not any of the doc tests. Use the nosetests command to run the full
    # test suite.
    test_suite='nose.collector'
)
