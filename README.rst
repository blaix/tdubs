TDubs
=====

A test double library for python.

Born out of my desire to use test doubles with these features:

1. Treat the double as a callable with return values specific to the arguments passed in.
2. Zero public attributes. To avoid conflicts with the object it's replacing in tests.
3. Ability to verify calls, after they are made, without risk of false-positives (explanation and feature coming soon).

Installation
------------

Coming soon. For now, just download ``tdubs.py``.

Usage
-----

.. code:: python

    from unittest import TestCase

    from tdubs import Double, calling
    
    # Some method I want to test that uses a collaborator
    def get_article(article_repo, article_id):
        return article_repo.get(article_id)

    class TestGetArticle(TestCase):
        def test_returns_article_from_repo_for_matching_id(self):
            repo, expected_article = Double(), Double()
            calling(repo.get).passing(123).returns(expected_article)

            article = get_article(repo, 123)

            self.assertEqual(article, expected_article)

See ``tdubs.Double`` for full usage.

Development
-----------

Clone the project.

Install dependencies::

    pip install -r requirements.txt

Run the tests::

    nosetests --with-doctest

Lint and test the code automatically when changes are made (see ``tube.py``)::

    stir
