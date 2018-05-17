from setuptools import find_packages, setup

# We need the following dependenices so that setup.py's command nosetests will
# run correclty without manually installing all dev dependencies. Note that
# these requirements cannot be specified as setup's tests_require param
# because tests_require dependencies are not installed before attempting to
# execute nosetests. nosetests is necessary because python setup.py test
# will not capture doctests.
setup_requires = ['nose==1.3.7', 'coverage==4.0.3']

setup(
    name='tdubs',
    version='0.3.0',
    url='https://github.com/blaix/tdubs',
    author='Justin Blake',
    author_email='justin@blaix.com',
    description='A test double library',
    packages=find_packages(),
    setup_requires=setup_requires,
    license='MIT (Expat)',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Testing',
    ],
    # The following allows the test command to find and execute unit tests
    # but not any of the doc tests. Use the nosetests command to run the full
    # test suite.
    test_suite='nose.collector',
    extras_require={
        'dev': [
            'coverage',
            'coveralls',
            'flake8',
            'flake8-quotes',
            'isort',
            'nose',
            'pep8',
            'testtube',
            'twine',
            'wheel',
        ],
    },
)
