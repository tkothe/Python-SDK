#-*- coding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]

.. autosummary::
    :nosignatures:

    Config
    YAMLConfig
    JSONConfig
"""
import base64
import json
import logging.config
import os

from .api import AboutYouException


class Config(object):
    """
    The configuration of a aboutyou api connection.

    A config class has to have the following readable attributes:

    :param entry_point_url: The url for aboutyou.
    :param app_id: The application id.
    :param app_token: The password aka token for the corresponding application id.
    :param app_secret: The secret of the appliction.
    :param agent: The name of the browser agent to fake.
    :param image_url: A string as template for the image urls.
                        As example http://cdn.mary-paul.de/file/{}.
    :param product_url: The template for a product.
    :param shop_url: The url template for the shop.
    :param javascript_url: The URL to the Collins JavaScript file for helper functions
                             to add product variants into the basket of Mary & Paul or auto-resizing
                             the Iframe. This URL may be changed in future, so please use this method instead
                             of hardcoding the URL into your HTML template.
    :param auto_fetch: If set True, Easyaboutyou fetches automaticly missing fields.
    :param cache: An dict {'hosts': ['server:11202'], 'timeout': 600}.
    :param dict logging: A dictonary for logging.config.dictConfig.
    """
    PARAMS = {"entry_point_url": "http://ant-shop-api1.wavecloud.de/api",
              "app_id": None,
              "app_token": None,
              "app_secret": None,
              "agent": "AboutYou-Shop-SDK-Python",
              "image_url": "http://cdn.mary-paul.de/file/{}",
              "product_url": "http://www.aboutyou.de/{}",
              "shop_url": "https://checkout.aboutyou.de/",
              "auto_fetch": True,
              "cache": None,
              "logging": None}

    def __init__(self, **kwargs):
        for key, value in Config.PARAMS.items():
            setattr(self, key, value)

        for key, value in kwargs.items():
            if key in Config.PARAMS:
                setattr(self, key, value)
            else:
                raise AboutYouException("unknown configuration key parameter")

        if "logging" in kwargs:
            logging.config.dictConfig(kwargs["logging"])

    @property
    def authorization(self):
        """
        Content for the authorization header.
        """
        data = "{}:{}".format(self.app_id, self.app_token)
        encoded = base64.b64encode(data)
        return "Basic " + encoded.decode("ascii")


    @property
    def javascript_tag(self):
        return '<script type="text/javascript" src="' + self.javascript_url + '"></script>'


class JSONConfig(Config):
    """
    Uses a JSON file for configuration.

    :param jsonfile: The path to the json configuration file.

    .. literalinclude:: ../config.json
        :language: json
    """
    def __init__(self, filename):
        with open(filename) as cfgfile:
            self.data = json.load(cfgfile)

        if "logging" in self.data and self.data["logging"] is not None:
            logging.config.dictConfig(self.data["logging"])

    def __getattr__(self, name):
        return self.data.get(name, None)


try:
    import yaml

    class YAMLConfig(Config):
        """
        Uses a YAML file for configuration.

        :param yamlfile: The path to the yaml configuration file.

        .. literalinclude:: ../config.yaml
            :language: yaml
        """
        def __init__(self, filename):
            with open(filename) as cfgfile:
                self.data = yaml.load(cfgfile)

            if "logging" in self.data and self.data["logging"] is not None:
                logging.config.dictConfig(self.data["logging"])

        def __getattr__(self, name):
            return self.data.get(name, None)
except ImportError:
    # No YAML config :(
    pass


class JSONEnvironmentFallbackConfig(Config):
    """
    This is the real hot shit.
    If a config value is not found in the JSON config, the given environment
    variable is used instead.

    :param jsonfile: The path to the json configuration file.

    .. code-block:: python

        # if the field *authorization* is not present in the config file,
        # then the environment variable *aboutyou_AUTH* will be used for the
        # config variable authorization.
        conf = JSONEnvironmentFallbackConfig('myconf.json', authorization='aboutyou_AUTH')
    """
    def __init__(self, jsonfile, **kwargs):
        with open(jsonfile) as cfgfile:
            self.data = json.load(cfgfile)

        for key, value in kwargs.items():
            if key not in Config.PARAMS:
                raise AboutYouException("unknown configuration key parameter")

            if key not in self.data:
                self.data[key] = os.environ[value]

        if "logging" in self.data and self.data["logging"] is not None:
            logging.config.dictConfig(self.data["logging"])

    def __getattr__(self, name):
        return self.data[name]
