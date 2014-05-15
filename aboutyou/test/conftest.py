#-*- coding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
import pytest

from aboutyou import YAMLConfig, Aboutyou
from aboutyou.easy import EasyAboutYou


config = YAMLConfig('slice-dice.yaml')


@pytest.fixture(scope='session')
def aboutyou():
    return Aboutyou(config)


@pytest.fixture(scope='session')
def easy():
    return EasyAboutYou(config)


@pytest.fixture
def session():
    return 's3ss10n'


@pytest.fixture
def log(request, aboutyou):
    return aboutyou.log.getChild(request.function.__name__)
