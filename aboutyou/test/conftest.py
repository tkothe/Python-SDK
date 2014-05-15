#-*- coding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
import pytest

from collins import YAMLConfig, Collins
from collins.easy import EasyCollins


config = YAMLConfig('slice-dice.yaml')


@pytest.fixture(scope='session')
def collins():
    return Collins(config)


@pytest.fixture(scope='session')
def easy():
    return EasyCollins(config)


@pytest.fixture
def session():
    return 's3ss10n'


@pytest.fixture
def log(request, collins):
    return collins.log.getChild(request.function.__name__)
