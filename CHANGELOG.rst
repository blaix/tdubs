DEV
====

* Add ``patch.stub`` and ``patch.spy``

0.3.0
======

* Renamed ``Mock`` to ``Spy``
* setup.py now properly indicates all of the depepdencies that are necessary
  to run its commands (test and nosetests were broken)
* Updated the manifest so that the test suite and the changelog are
  included in dists.
* Officially drop support for Python 2. It may work in python 2, but I will no
  longer be testing it.

0.2.0
=====

* **Feature:** Raise exceptions from stubbed calls with ``.raises(exception)``
* ``.returns()`` can now be called without arguments to stub a call that returns nothing.
* Officially support Python 2

0.1.2
=====

* Initial release supporting ``Stub``, ``Mock``, ``calling``, and ``verify``.
