"""Unit tests for the TF-IDF backend in Annif"""

import annif
import annif.backend
import annif.corpus
from sklearn.feature_extraction.text import TfidfVectorizer
import pytest
import unittest.mock


def test_tfidf_default_params(project):
    tfidf_type = annif.backend.get_backend("tfidf")
    tfidf = tfidf_type(
        backend_id='tfidf',
        config_params={},
        project=project)

    expected_default_params = {
        'limit': 100  # From AnnifBackend class
    }
    actual_params = tfidf.params
    for param, val in expected_default_params.items():
        assert param in actual_params and actual_params[param] == val


def test_tfidf_train(datadir, document_corpus, project):
    tfidf_type = annif.backend.get_backend("tfidf")
    tfidf = tfidf_type(
        backend_id='tfidf',
        config_params={'limit': 10},
        project=project)

    tfidf.train(document_corpus)
    assert len(tfidf._index) > 0
    assert datadir.join('tfidf-index').exists()
    assert datadir.join('tfidf-index').size() > 0


def test_tfidf_suggest(project):
    tfidf_type = annif.backend.get_backend("tfidf")
    tfidf = tfidf_type(
        backend_id='tfidf',
        config_params={'limit': 10},
        project=project)

    results = tfidf.suggest("""Arkeologiaa sanotaan joskus myös
        muinaistutkimukseksi tai muinaistieteeksi. Se on humanistinen tiede
        tai oikeammin joukko tieteitä, jotka tutkivat ihmisen menneisyyttä.
        Tutkimusta tehdään analysoimalla muinaisjäännöksiä eli niitä jälkiä,
        joita ihmisten toiminta on jättänyt maaperään tai vesistöjen
        pohjaan.""")

    assert len(results) == 10
    assert 'http://www.yso.fi/onto/yso/p1265' in [
        result.uri for result in results]
    assert 'arkeologia' in [result.label for result in results]


def test_suggest_cli_param_limit(project):
    tfidf_type = annif.backend.get_backend("tfidf")
    tfidf = tfidf_type(
        backend_id='tfidf',
        config_params={'limit': 10},
        project=project)
    cli_params = {'tfidf': {'limit': 3}}

    results = tfidf.suggest("""Arkeologiaa sanotaan joskus myös
        muinaistutkimukseksi tai muinaistieteeksi. Se on humanistinen tiede
        tai oikeammin joukko tieteitä, jotka tutkivat ihmisen menneisyyttä.
        Tutkimusta tehdään analysoimalla muinaisjäännöksiä eli niitä jälkiä,
        joita ihmisten toiminta on jättänyt maaperään tai vesistöjen
        pohjaan.""", cli_params)

    assert len(results) == 3


def test_tfidf_suggest_unknown(project):
    tfidf_type = annif.backend.get_backend("tfidf")
    tfidf = tfidf_type(
        backend_id='tfidf',
        config_params={'limit': 10},
        project=project)

    results = tfidf.suggest("abcdefghijk")  # unknown word

    assert len(results) == 0
