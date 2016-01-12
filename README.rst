TDubs
=====

A test double library for python.

Born out of my desire to use test doubles with these features:

1. Treat the double as a callable with return values specific to the arguments passed in.
2. Zero public attributes. To avoid conflicts with the object it's replacing in tests.
3. Ability to verify calls, after they are made, without risk of false-positives

Installation
------------

Coming soon. For now, just download ``tdubs.py``.

Usage
-----

See ``tdubs.Double`` for full usage.

Development
-----------

Clone the project.

Install dependencies::

    pip install -r requirements.txt

Run the tests::

    nosetests --with-doctest --doctest-options=+ELLIPSIS

Lint and test the code automatically when changes are made (see ``tube.py``)::

    stir
