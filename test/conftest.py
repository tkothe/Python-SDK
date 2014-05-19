#-*- coding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
import pytest

from aboutyou import Config, Aboutyou
from aboutyou.easy import EasyAboutYou


config = Config(app_id=110, app_token='ed8272cc4d993378f595d112915920bb',
                logging={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {
                    "format": "%(asctime)s | %(levelname)-7s | %(name)-20s | %(message)s"
                }
            },
            "handlers": {
                "rotating": {
                    "level":"DEBUG",
                    "class":"logging.handlers.TimedRotatingFileHandler",
                    "formatter": "simple",
                    "when": "midnight",
                    "filename": "aboutyou.log"
                }
            },

            "loggers": {
                "aboutyou": {
                    "level": "DEBUG",
                    "handlers": ["rotating"]
                }
            },
            "root": {
                "handlers": [],
                "level": "DEBUG",
                "propagate": True
            }
        })


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
