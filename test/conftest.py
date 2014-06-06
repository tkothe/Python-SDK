#-*- coding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
import json
import os
import pytest

from aboutyou.api import Aboutyou
from aboutyou.config import YAMLConfig, YAMLCredentials
from aboutyou.easy import EasyAboutYou


config = YAMLConfig('config.yaml')
credentials = YAMLCredentials('slice-dice.yaml')


def read(filename):
    with open(os.path.join('test', 'data', filename)) as src:
        return src.read()


@pytest.fixture
def mock(monkeypatch):
    def wrapper(filename):
        def request(self, params):
            return read(filename)

        monkeypatch.setattr("aboutyou.api.Aboutyou.request", request)

        with open(os.path.join('test', 'data', filename)) as src:
            return json.load(src)

    return wrapper


@pytest.fixture
def aboutyou():
    return Aboutyou(config, credentials)


@pytest.fixture
def easy(monkeypatch):
    client = EasyAboutYou(config, credentials)

    monkeypatch.setattr("aboutyou.api.Aboutyou.request", lambda self, params: read('category-tree.json'))

    client.categories()

    monkeypatch.setattr("aboutyou.api.Aboutyou.request", lambda self, params: read('facets-all.json'))

    client.facet_groups()

    return client


@pytest.fixture
def session():
    return 's3ss10n'


@pytest.fixture
def log(request, aboutyou):
    return aboutyou.log.getChild(request.function.__name__)
