"""Example test from the README.

TODO: how to keep these in sync?

More ellaborate tests are in doctests in tdubs.py

"""
from unittest import TestCase

from tdubs import Double, calling


def get_article(article_repo, article_id):
    return article_repo.get(article_id)


class TestGetArticle(TestCase):
    def test_returns_article_from_repo_for_matching_id(self):
        repo, expected_article = Double(), Double()
        calling(repo.get).passing(123).returns(expected_article)

        article = get_article(repo, 123)

        self.assertEqual(article, expected_article)
