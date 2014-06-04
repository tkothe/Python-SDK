#-*- coding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
import pytest

from aboutyou.api import Aboutyou
from aboutyou.config import YAMLConfig, YAMLCredentials
from aboutyou.easy import EasyAboutYou


config = YAMLConfig('config.yaml')
credentials = YAMLCredentials('slice-dice.yaml')


@pytest.fixture(scope='session')
def aboutyou():
    return Aboutyou(config, credentials)


@pytest.fixture(scope='session')
def easy():
    return EasyAboutYou(config, credentials)


@pytest.fixture
def session():
    return 's3ss10n'


@pytest.fixture
def log(request, aboutyou):
    return aboutyou.log.getChild(request.function.__name__)
