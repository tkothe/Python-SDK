#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
from collins.test import TEST_CONFIG
import collins


class TestConfig:
    def testNameResolution(self):
        conf = collins.JSONConfig(TEST_CONFIG)

        assert conf.app_id is not None

    def testImageName(self):
        name = "http://cdn.mary-paul.de/file/0"
        conf = collins.JSONConfig(TEST_CONFIG)

        assert conf.imageurl(0) == name
