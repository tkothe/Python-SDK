#-*- coding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
import pytest

from aboutyou import Config, Aboutyou
from aboutyou.easy import EasyAboutYou


config = Config(app_id=110, app_token='ed8272cc4d993378f595d112915920bb')


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
