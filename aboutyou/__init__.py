#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]

This module provieds two wrappers around the AboutYou-Shop-API.

* A thin python wrapper which takes Python dict's and list's and returns the
  result as the same.
* Easyaboutyou, which is a more convient layer of abstraction of the API as an
  object herachie which caches results and query results if there are needed.


.. autosummary::
    :nosignatures:

    Config
    Aboutyou
    YAMLConfig
    JSONConfig
"""
import time
import base64
import json
import logging
import logging.config
import urllib2
import os


ABOUTYOU_VERSION = "1.1"
"""The version of the aboutyou api which is supported."""

VERSION = "0.3.2"
"""Version of the python shop SDK."""

AUTHORS = [
    "Arne Simon [arne_simon@slice-dice.de]"
]


class AboutYouException(Exception):
    """An exception in the aboutyou module."""
    pass


class Constants(object):
    """
    Some contsants which are blatantly copied from the php-sdk.
    """
    FACET_BRAND = 0
    FACET_CLOTHING_MEN_BELTS_CM = 190
    FACET_CLOTHING_MEN_DE = 187
    FACET_CLOTHING_MEN_INCH = 189
    FACET_CLOTHING_UNISEX_INCH = 174
    FACET_CLOTHING_UNISEX_INT = 173
    FACET_CLOTHING_UNISEX_ONESIZE = 204
    FACET_CLOTHING_WOMEN_BELTS_CM = 181
    FACET_CLOTHING_WOMEN_DE = 175
    FACET_CLOTHING_WOMEN_INCH = 180
    FACET_COLOR = 1
    FACET_CUPSIZE = 4
    FACET_DIMENSION3 = 6
    FACET_GENDERAGE = 3
    FACET_LENGTH = 5
    FACET_SHOES_UNISEX_ADIDAS_EUR = 195
    FACET_SHOES_UNISEX_EUR = 194
    FACET_SIZE = 2
    FACET_SIZE_CODE = 206
    FACET_SIZE_RUN = 172
    # not in the PHP-SDK o.O ?
    # FACET_CHANNEL = 211
    # FACET_CARE_SYMBOL = 247
    # FACET_CLOTHING_HATS_US = 231

    FACETS = set([FACET_BRAND, FACET_CLOTHING_MEN_BELTS_CM, FACET_CLOTHING_MEN_DE, FACET_CLOTHING_MEN_INCH,
                 FACET_CLOTHING_UNISEX_INCH, FACET_CLOTHING_UNISEX_INT, FACET_CLOTHING_UNISEX_ONESIZE,
                 FACET_CLOTHING_WOMEN_BELTS_CM, FACET_CLOTHING_WOMEN_DE, FACET_CLOTHING_WOMEN_INCH, FACET_COLOR,
                 FACET_CUPSIZE, FACET_DIMENSION3, FACET_GENDERAGE, FACET_LENGTH, FACET_SHOES_UNISEX_ADIDAS_EUR,
                 FACET_SHOES_UNISEX_EUR, FACET_SIZE, FACET_SIZE_CODE, FACET_SIZE_RUN,
                 ])

    SORT_CREATED = "created_date"
    SORT_MOST_VIEWED = "most_viewed"
    SORT_PRICE = "price"
    SORT_RELEVANCE = "relevance"
    SORT_UPDATED = "updated_date"
    SORTS = set([SORT_RELEVANCE, SORT_UPDATED, SORT_CREATED,
                 SORT_MOST_VIEWED, SORT_PRICE])

    TYPE_CATEGORIES = "categories"
    TYPE_PRODUCTS = "products"
    TYPES = set([TYPE_CATEGORIES, TYPE_PRODUCTS])

    PRODUCT_FIELD_VARIANTS = "variants"
    PRODUCT_FIELD_DESCRIPTION_LONG = "description_long"
    PRODUCT_FIELD_DESCRIPTION_SHORT = "description_short"
    PRODUCT_FIELD_MIN_PRICE = "min_price"
    PRODUCT_FIELD_MAX_PRICE = "max_price"
    PRODUCT_FIELD_SALE = "sale"
    PRODUCT_FIELD_DEFAULT_VARIANT = "default_variant"
    PRODUCT_FIELD_DEFAULT_IMAGE = "default_image"
    PRODUCT_FIELD_CATEGORIES = "categories"
    PRODUCT_FIELDS = set([PRODUCT_FIELD_VARIANTS, PRODUCT_FIELD_DESCRIPTION_LONG,
                        PRODUCT_FIELD_DESCRIPTION_SHORT, PRODUCT_FIELD_MIN_PRICE,
                        PRODUCT_FIELD_MAX_PRICE, PRODUCT_FIELD_SALE,
                        PRODUCT_FIELD_DEFAULT_VARIANT, PRODUCT_FIELD_DEFAULT_IMAGE,
                        PRODUCT_FIELD_CATEGORIES,])


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
    :param auto_fetch: If set True, Easyaboutyou fetches automaticly missing fields.
    :param cache: An array of Memcached servers.
    :param dict logging: A dictonary for logging.config.dictConfig.
    """
    PARAMS = {
                "entry_point_url": "http://ant-shop-api1.wavecloud.de/api",
                "app_id": None,
                "app_token": None,
                "app_secret": None,
                "agent": "AboutYou-Shop-SDK-Python",
                "image_url": "http://cdn.mary-paul.de/file/{}",
                "product_url": "http://www.aboutyou.de/{}",
                "shop_url": "https://checkout.aboutyou.de/",
                "auto_fetch": True,
                "cache": None,
                "logging": None
            }

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
except:
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

        loc = locals()
        for key, value in kwargs.items():
            if key not in Config.PARAMS:
                raise AboutYouException("unknown configuration key parameter")

            if key not in self.data:
                if loc[key] is not None:
                    self.data[key] = os.environ[loc[key]]
                else:
                    msg = 'config value "{}" not present'.format(key)
                    raise AboutYouException(msg)

        if "logging" in self.data and self.data["logging"] is not None:
            logging.config.dictConfig(self.data["logging"])

    def __getattr__(self, name):
        return self.data[name]


def check_sessionid(sessionid):
    """
    .. note::
        We copied it from the php-sdk.
        aboutyou seems to want, to have the session-id with a minimum length of
        five characters. This is not tested or validated.
    """
    if len(sessionid) < 5:
        raise AboutYouException("The session id must have at least 5 characters")


class Aboutyou(object):
    """
    An interface to the aboutyou API.

    This is thin warper around the aboutyou API.
    All functions return the JSON responses as Python List and Dictonarys.

    :param config: A Config instance.

    .. rubric:: Example

    .. code-block:: python

        >>> from aboutyou import Aboutyou, Constants, YAMLConfig
        >>> c =  Aboutyou(YAMLConfig("myconfig.yml"))
        >>> c.facets([Constants.FACET_CUPSIZE])

    .. code-block:: json

        {
            "facet": [
                {
                    "id": 4,
                    "group_name": "cupsize",
                    "name": "D",
                    "value": "D",
                    "facet_id": 96
                },
                {
                    "id": 4,
                    "group_name": "cupsize",
                    "name": "A",
                    "value": "A",
                    "facet_id": 93
                },
                {
                    "id": 4,
                    "group_name": "cupsize",
                    "name": "B",
                    "value": "B",
                    "facet_id": 94
                },
                {
                    "id": 4,
                    "group_name": "cupsize",
                    "name": "C",
                    "value": "C",
                    "facet_id": 95
                }
            ],
            "hits": 4
        }
    """

    def __init__(self, config):
        self.config = config

        logname = "aboutyou.{}".format(self.config.app_id)
        self.log = logging.getLogger(logname)
        self.log.debug("instantiated")

    def send(self, cmd, obj):
        """
        Sends a Pyhton structure of dict's and list's as raw JSON to aboutyou and
        returns a Python structure of dict's and list's from the JSON answer.

        :param cmd: The name of the command.
        :param obj: A python dict object which contains the request parameters.
        :returns: A JSON structure as python dicts and lists.
        """
        params = json.dumps([{cmd: obj}])
        headers = {
            "Content-Type": "text/plain;charset=UTF-8",
            "User-Agent": self.config.agent,
            "Authorization": self.config.authorization,
        }

        try:
            req = urllib2.Request(self.config.entry_point_url, params, headers)
            response = urllib2.urlopen(req)

            result = response.read()
            result = json.loads(result, encoding="utf-8")[0][cmd]

            if "error_message" in result:
                self.log.error(result["error_message"])
                raise AboutYouException(result["error_message"])

            return result

        except urllib2.HTTPError as err:
            message = "{} {} {}".format(err.code, err.msg, err.read())
            self.log.exception(message)
            raise AboutYouException(message)
        except urllib2.URLError as err:
            self.log.exception('')
            raise AboutYouException(err.reason)

    def autocomplete(self, searchword, limit=None, types=None):
        """
        :param str searchword: The abbriviation.
        :param list types: against which types should be autocompleted.
                            The oprions are :py:class:`aboutyou.Constants.TYPES`
        :param int limit: the amount of items returned per selected type
        :returns: A dict with "products" and/or "categories".

        .. code-block:: python

            >>> aboutyou.autocomplete("sho", types=[Constants.TYPE_PRODUCTS])

        .. code-block:: json

            {
                "products": [
                    {
                        "min_price": 5995,
                        "name": "Shopper mit Innenfutter in Leo-Print",
                        "sale": false,
                        "id": 303058,
                        "brand_id": 163,

                        "even more": "product stuff but its only",
                        "a short example": "}:->"
                    }
                ]
            }

        """
        complete = {"searchword": searchword}

        if limit is not None:
            if limit < 1 or limit > 200:
                raise AboutYouException("limit out of range")

            complete["limit"] = limit

        if types is not None:
            if len(set(types) - Constants.TYPES) > 0:
                raise AboutYouException("unknown types")

            complete["types"] = types

        return self.send("autocompletion", complete)

    def basket_set(self, sessionid, variants):
        """
        :param str sessionid: identification of the basket -> user, user -> basket
        :param list variants: is the array of tuples. (<someid>, <variant id>) or (<someid>, <variant id>, <additional data>)
        :returns: The basket JSON.

        .. note::

        If you supply additional data to costumize a variant. You **have to** have
        the field *description* present!

        .. code-block:: python

            >>> data = [('my4813890', 4813890), ('my4813890', 4813890, {'description': 'costum stuff'})]
            >>> aboutyou.basketset('someid', data)

        .. code-block:: json

            {
                "order_lines": [
                    {
                        "total_price": 1999,
                        "product_id": 234526,
                        "tax": 19.0,
                        "total_net": 1680,
                        "total_vat": 319,
                        "variant_id": 4813890,
                        "id": "my4813890"
                    }
                ],
                "total_price": 1999,
                "products": {
                    "234526": {
                        "name": "Bikinislip, LASCANA (3 Stck.)",
                        "sale": false,
                        "brand_id": 266,
                        "categories.110": [
                            [
                                19532,
                                19540,
                                19615
                            ]
                        ],
                        "description_long": "Superangenehm zu tragen dank besonders ",
                        "active": true,
                        "variants": [
                            {
                                "updated_date": "2014-05-14 12:03:42",
                                "first_active_date": "2014-02-27 15:35:57",
                                "default": false,
                                "old_price": 0,
                                "price": 1999,
                                "ean": "369969656",
                                "first_sale_date": null,
                                "id": 4813890,
                                "created_date": "2013-12-07 11:23:36",
                                "images": [
                                    {
                                        "mime": "image/jpeg",
                                        "image": {
                                            "width": 672,
                                            "height": 960
                                        },
                                        "hash": "7b36192b57368bd54a8be3660098f1bc",
                                        "ext": ".jpg",
                                        "size": 72776
                                    }
                            }
                        ],
                        "description_short": "Superangenehm zu tragen dank besonders",
                        "id": 234526
                    }
                },
                "total_vat": 319,
                "total_net": 1680
            }
        """
        check_sessionid(sessionid)

        def build(var):
            length = len(var)

            if length == 2:
                return {'id':var[0], 'variant_id':var[1]}
            elif length == 3:
                # return {'id':var[0], 'variant_id':var[1]}
                return {'id':var[0], 'variant_id':var[1], 'additional_data': var[2]}


        data = {
                "session_id": sessionid,
                "order_lines": [build(var) for var in variants]
            }

        # self.log.debug(json.dumps(data, indent=4))

        return self.send("basket", data)

    def basket_get(self, sessionid):
        """
        This returns the current basket for a User / Session ID.
        The basket belongs to a specific app id and session id,
        another app can have the same session id.

        :param str sessionid: identification of the basket -> user,
                              user -> basket

        .. code-block:: python

            >>> aboutyou.basketget('someid')

        .. code-block:: json

            {
                "order_lines": [
                    {
                        "total_price": 1999,
                        "product_id": 234526,
                        "tax": 19.0,
                        "total_net": 1680,
                        "total_vat": 319,
                        "variant_id": 4813890,
                        "id": "my4813890"
                    }
                ],
                "total_price": 1999,
                "products": {
                    "234526": {
                        "name": "Bikinislip, LASCANA (3 Stck.)",
                        "sale": false,
                        "brand_id": 266,
                        "categories.110": [
                            [
                                19532,
                                19540,
                                19615
                            ]
                        ],
                        "description_long": "Superangenehm zu tragen dank besonders ",
                        "active": true,
                        "variants": [
                            {
                                "updated_date": "2014-05-14 12:03:42",
                                "first_active_date": "2014-02-27 15:35:57",
                                "default": false,
                                "old_price": 0,
                                "price": 1999,
                                "ean": "369969656",
                                "first_sale_date": null,
                                "id": 4813890,
                                "created_date": "2013-12-07 11:23:36",
                                "images": [
                                    {
                                        "mime": "image/jpeg",
                                        "image": {
                                            "width": 672,
                                            "height": 960
                                        },
                                        "hash": "7b36192b57368bd54a8be3660098f1bc",
                                        "ext": ".jpg",
                                        "size": 72776
                                    }
                            }
                        ],
                        "description_short": "Superangenehm zu tragen dank besonders",
                        "id": 234526
                    }
                },
                "total_vat": 319,
                "total_net": 1680
            }

        """
        check_sessionid(sessionid)

        return self.send("basket", {"session_id": sessionid})

    def basket_remove(self, sessionid, variants):
        """
        Removes elements from the basket associated with the session id.

        :param sessionid: The session associated with the basket.

        .. code-block:: python

            >>> aboutyou.basketremove('someid', ['my4813890'])

        .. code-block:: json

            {
                "order_lines": [
                    {
                        "total_price": 1999,
                        "product_id": 234526,
                        "tax": 19.0,
                        "total_net": 1680,
                        "total_vat": 319,
                        "variant_id": 4813890,
                        "id": "my4813890"
                    }
                ],
                "total_price": 1999,
                "products": {
                    "234526": {
                        "name": "Bikinislip, LASCANA (3 Stck.)",
                        "sale": false,
                        "brand_id": 266,
                        "categories.110": [
                            [
                                19532,
                                19540,
                                19615
                            ]
                        ],
                        "description_long": "Superangenehm zu tragen dank besonders ",
                        "active": true,
                        "variants": [
                            {
                                "updated_date": "2014-05-14 12:03:42",
                                "first_active_date": "2014-02-27 15:35:57",
                                "default": false,
                                "old_price": 0,
                                "price": 1999,
                                "ean": "369969656",
                                "first_sale_date": null,
                                "id": 4813890,
                                "created_date": "2013-12-07 11:23:36",
                                "images": [
                                    {
                                        "mime": "image/jpeg",
                                        "image": {
                                            "width": 672,
                                            "height": 960
                                        },
                                        "hash": "7b36192b57368bd54a8be3660098f1bc",
                                        "ext": ".jpg",
                                        "size": 72776
                                    }
                            }
                        ],
                        "description_short": "Superangenehm zu tragen dank besonders",
                        "id": 234526
                    }
                },
                "total_vat": 319,
                "total_net": 1680
            }
        """
        check_sessionid(sessionid)

        if len(variants) < 1:
            raise AboutYouException('No ids submitted.')

        data = {"session_id": sessionid,
                "order_lines": [{"delete": str(vid)} for vid in variants]}

        # self.log.debug(json.dumps(data, indent=4))

        return self.send("basket", data)

    def basket_dispose(self, sessionid):
        """
        Deletes all items in the basket.

        :param sessionid: The session associated with the basket.
        """
        check_sessionid(sessionid)

        data = self.basket_get(sessionid)

        vids = [order['id'] for order in data['order_lines']]

        self.basket_remove(sessionid, vids)

    def category(self, ids):
        """
        You are able to retrieve single categories.

        :param list ids: List of category ids.

        .. code-block:: python

            >>> aboutyou.category([16077])

        .. code-block:: json

            {
                "16077": {
                    "active": true,
                    "position": 1,
                    "name": "Damen",
                    "parent": 0,
                    "id": 16077
                }
            }
        """
        idscount = len(ids)

        if idscount < 1:
            raise AboutYouException("to few ids")

        if idscount > 200:
            raise AboutYouException("to many ids, maximum is 200")

        return self.send("category", {"ids": ids})

    def categorytree(self, max_depth=None):
        """
        The request category tree returns a tree of categories of a
        specified max depth for your app id.

        :param int max_depth: max depth of your category tree counted from root

        .. code-block:: python

            >>> aboutyou.categorytree()

        .. code-block:: json

            [
                {
                    "name": "Damen",
                    "parent": null,
                    "active": false,
                    "position": 1,
                    "id": 16077,
                    "sub_categories": [
                        {
                            "name": "Bekleidung",
                            "parent": 16077,
                            "active": false,
                            "position": 1,
                            "id": 16078,
                            "sub_categories": [
                                {
                                    "name": "Oberteile",
                                    "parent": 16078,
                                    "active": false,
                                    "position": 1,
                                    "id": 16079,
                                    "sub_categories": [
                                        {
                                            "name": "Fr\u00fchlingslooks",
                                            "parent": 16079,
                                            "sub_categories": [],
                                            "active": false,
                                            "position": 1,
                                            "id": 23882
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        """
        if max_depth is None:
            cmd = {}
        else:
            if max_depth < -1:
                raise AboutYouException("max_depth to small")

            if max_depth > 10:
                raise AboutYouException("max_depth to big")

            cmd = {"max_depth": max_depth}

        return self.send("category_tree", cmd)

    def facets(self, group_ids=None, limit=None, offset=None):
        """
        This returns a list of available facet groups or a facets of a group.

        :param list group_ids: get only these group ids, if empty get all
                                group ids which belong to me
        :param int limit: limit the per page items
        :param int offset: offset for paging through the items

        .. code-block:: python

            >>> aboutyou.facets([Constants.FACET_CUPSIZE])

        .. code-block:: json

            {
                "facet": [
                    {
                        "id": 4,
                        "group_name": "cupsize",
                        "name": "D",
                        "value": "D",
                        "facet_id": 96
                    },
                    {
                        "id": 4,
                        "group_name": "cupsize",
                        "name": "A",
                        "value": "A",
                        "facet_id": 93
                    },
                    {
                        "id": 4,
                        "group_name": "cupsize",
                        "name": "B",
                        "value": "B",
                        "facet_id": 94
                    },
                    {
                        "id": 4,
                        "group_name": "cupsize",
                        "name": "C",
                        "value": "C",
                        "facet_id": 95
                    }
                ],
                "hits": 4
            }
        """
        facets = {}

        if limit is not None:
            if limit < 1:
                raise AboutYouException("limit is to small")

            facets["limit"] = limit

        if group_ids is not None:
            facets["group_ids"] = group_ids

        if offset is not None:
            if offset < 0:
                raise AboutYouException('offset out of range')

            facets["offset"] = offset

        return self.send("facets", facets)

    def facettypes(self):
        """
        This query returns a list of facet groups available.

        .. code-block:: python

            >>> aboutyou.facettypes()

        .. code-block:: json

            [0, 2, 1, 6, 172, 206, 173, 194, 175, 204, 5, 189, 180, 231, 187, 190, 211, 181, 247]
        """

        return self.send("facet_types", {})

    # def getorder(self, orderid):
    #     """Through this query you could get a order which was created
    #         for/through your app. This is limited to a configured
    #         timeframe and to your app.

    #     :param int orderid: this is the order id to get info about
    #     :returns: Order JSON
    #     """
    #     return self.send("get_order", {"order_id": orderid})

    def order(self, sessionid, success_url,
              cancel_url=None, error_url=None):
        """
        At this request you initiate a order to a basket.
        This should be done if a user wants to go to the checkout.

        :param str sessionid: identification of the basket -> user,
                              user -> basket (see basket_get, basket_add)
        :param str success_url: this is a callback url if the order was
                               successfully created. (see checkout api)
        :param str cancel_url: this is a callback url if the order was
                               canceled. (see checkout api)
        :param str error_url: this is a callback url if the order throwed
                              exceptions (see checkout api)
        :returns: An url to the shop.
        """
        check_sessionid(sessionid)

        order = {"session_id": sessionid, "success_url": success_url}

        if cancel_url is not None:
            order["cancel_url"] = cancel_url

        if error_url is not None:
            order["error_url"] = error_url

        response = self.send("initiate_order", order)

        # the url in response["url"] seems to be invalid !!!

        params = '?user_token={}&app_token={}&basketId={}&appId={}'
        params = params.format(response["user_token"], response["app_token"],
                               sessionid, self.config.app_id)

        return self.config.shop_url + params

    def livevariant(self, ids):
        """
        This does return the live information about the product variant.
        This is as "live" as possible.
        And could differ vs. a "product search" or "product" query.

        :param list ids: array of product variant id

        .. code-block:: python

            >>> aboutyou.livevariant([4760437])

        .. code-block:: json

            {
                "4760437": {
                    "available_stock": 999,
                    "price": 3995,
                    "id": 4760437,
                    "product_id": 223910
                }
            }
        """
        idscount = len(ids)

        if idscount < 1:
            raise AboutYouException("too few ids")

        if idscount > 200:
            raise AboutYouException("too many ids")

        return self.send("live_variant", {"ids": ids})

    def products(self, ids, fields=None):
        """
        Here you get a detail view of a product or a list of products returned
        by its ids.

        :param list ids: array of product id
        :param list fields: list of field names

        .. rubric:: Possible Field Options

        .. hlist::
            :columns: 3

            * variants
            * description_long
            * description_short
            * min_price
            * max_price
            * sale
            * default_variant
            * default_image
            * id
            * name
            * active
            * attributes_merged
            * categorie

        .. rubric:: Example

        .. code-block:: python

            >>> aboutyou.products(ids=[227838, 287677], fields=["variants"])

        .. code-block:: json

            {
                "pageHash": "4ae38022-8ddd-4f15-9654-4ea0156c33f0",
                "ids": {
                    "287677": {
                        "active": true,
                        "styles": [
                            {
                                "active": true,
                                "id": 287685,
                                "style_key": "m01_233966406",
                                "name": "Badeshorts, Buffalo"
                            },
                            {
                                "active": false,
                                "id": 358863,
                                "style_key": "m01_233966406",
                                "name": "Badeshorts, Buffalo"
                            }
                        ],
                        "id": 287677,
                        "style_key": "m01_233966406",
                        "name": "Badeshorts, Buffalo"
                    },
                    "227838": {
                        "active": true,
                        "styles": [
                            {
                                "active": true,
                                "id": 227854,
                                "style_key": "m01_255897631",
                                "name": "Badeshort Herren"
                            }
                        ],
                        "id": 227838,
                        "style_key": "m01_255897631",
                        "name": "Badeshort Herren"
                    }
                }
            }
        """
        products = {}

        count = len(ids)

        if count < 1:
            raise AboutYouException("too few ids")

        if count > 200:
            raise AboutYouException("too many ids")

        products["ids"] = ids

        if fields is not None:
            products["fields"] = fields

        return self.send("products", products)

    def producteans(self, eans, fields=None):
        """
        Returns products by eans.

        :param list eans: An array of eans.
        :returns: Array of products.
        """
        products = {}

        count = len(eans)

        if count < 1:
            raise AboutYouException("too few eans")

        if count > 200:
            raise AboutYouException("too many eans")

        # aboutyou wants eans as strings
        products["eans"] = [str(e) for e in eans]

        if fields is not None:
            products["fields"] = fields

        return self.send("products_eans", products)["eans"]

    def productsearch(self, sessionid, filter=None, result=None):
        """
        This is the main query for retrieving products for your app.
        Lists of products will be returned which are filtered.
        In a search you dont get back inactive set products.
        The response can contain the available facets and their product count
        and categories for the filter set.

        There are two types of facets:
            1. is a pre defined and always available set of facets
                a. price range (amazon like see )
                b. sale facet how many products are sale and how many not
                c. categories
            2. dynamic facets which occur through the products itself. If a
               product has one the these attributes you are able to query for
               these attributes. These facets are always just ids.
               The name -> id, id -> name resolution works through facets call.
               To get all the facet groups you can filter or are in your result
               set see "Facet types"

        .. note::
            To get facet types see :py:class:`aboutyou.Constants`

        :param str sessionid: the session_id of the frontend customer
        :param dict filter: object of filter information, these filters do
                            change the subset of products
        :param dict result: object of result information, these properties
                            change the order and the appearance of the subset

        .. rubric:: filter dict

        +----------+-------------------------------------------------------+
        |fieldname |                     meaning                           |
        +==========+=======================================================+
        |categories|array of category ids to include the products from     |
        +----------+-------------------------------------------------------+
        |sale      |true => only sale products                             |
        |          |false => no sale products                              |
        |          |null => both                                           |
        +----------+-------------------------------------------------------+
        |prices    |is an object with properties from and to which lead to |
        |          |range filter on the price set as eurocent              |
        +----------+-------------------------------------------------------+
        |searchword|the word which filters every product                   |
        +----------+-------------------------------------------------------+
        |facets    |object of attributes every key is an array of facet id |
        |          |values to filter by them                               |
        +----------+-------------------------------------------------------+

        .. rubric:: result dict

        +----------+-----------------------------------------------------------+
        |fieldname |                         meaning                           |
        +==========+===========================================================+
        |sort      |how to sort the products                                   |
        +----------+-----------------------------------------------------------+
        |price     |geta back a range of attributes and their product counts   |
        |          |also some statistical information in eurocent.             |
        +----------+-----------------------------------------------------------+
        |sale      |product count of products which are in sale                |
        +----------+-----------------------------------------------------------+
        |facets    |object of which facet get back what count of facets        |
        +----------+-----------------------------------------------------------+
        |fields    | array of product field names                              |
        +----------+-----------------------------------------------------------+
        |categories|set if get or not back the categories in which are products|
        |          |and the count of products                                  |
        +----------+-----------------------------------------------------------+
        |limit     |how many products to get back                              |
        +----------+-----------------------------------------------------------+
        |offset    |the offset where to start to get the products from         |
        +----------+-----------------------------------------------------------+

        .. rubric:: result.facets dict

        +---------+----------------------------------------------------------+
        |fieldname|                         meaning                          |
        +=========+==========================================================+
        |_all     |is an object with property limit which holds an integer   |
        |         |to get the amount of attributes, sort by occurrences in   |
        |         |products if this is set, this is the default for          |
        |         |ALL attributes.                                           |
        +---------+----------------------------------------------------------+
        |[ 0-9 ]+ |is an object with property limit which holds an integer to|
        |         |get the amount of attributes of this attribute group id,  |
        |         |sort by occurrences in products. this overwrites even the |
        |         |_all field.                                               |
        +---------+----------------------------------------------------------+


        .. rubric:: Example

        .. code-block:: python

            >>> aboutyou.productsearch(TEST_SESSION_ID, filter={"categories":[16354]})

        .. code-block:: json

            {
                "product_count": 78,
                "pageHash": "6e63cadb-5505-47b7-b36d-643311292a22",
                "facets": {},
                "products": [
                    {
                        "id": 227838,
                        "name": "Badeshort Herren"
                    }
                ]
            }

        .. code-block:: python

            >>> filter={"sale":True}
            >>> result={"sale":True, "limit":2}
            >>> aboutyou.productsearch("sessionid", filter=filter, result=result)

        .. code-block:: json

            {
                "product_count": 5866,
                "pageHash": "c54cc835-2b2f-448b-84a8-ef1e23fa7280",
                "facets": {
                    "sale": {
                        "_type": "terms",
                        "total": 29797,
                        "terms": [
                            {
                                "count": 23931,
                                "term": "0"
                            },
                            {
                                "count": 5866,
                                "term": "1"
                            }
                        ],
                        "other": 0,
                        "missing": 0
                    }
                },
                "products": [
                    {
                        "id": 297395,
                        "name": "Fischer Skihose, \u00bbLimit\u00ab"
                    },
                    {
                        "id": 300068,
                        "name": "Armbanduhr, Esprit, \u00bbglamonza silver ES105432004\u00ab"
                    }
                ]
            }
        """
        check_sessionid(sessionid)

        search = {"session_id": sessionid}

        if filter is not None:
            search["filter"] = filter

        if result is not None:
            search["result"] = result

        return self.send("product_search", search)

    def suggest(self, searchword, categories=None, limit=None):
        """
        The suggest endpoint does what it says and suggest more terms.
        It takes a searchterm and suggests terms which occurance is really
        often in combination with these terms before.

        :param str searchword: string of a searchterm to suggest more words for
        :param list categories: array of category ids
        :param int limit: amount of items to suggest
        :returns: A list of strings.
        """
        suggest = {"searchword": searchword}

        if categories is not None:
            suggest["categories"] = categories

        if limit is not None:
            if limit < 1 or limit > 200:
                raise AboutYouException('The limit has to between 1 and 200.')

            suggest["limit"] = limit

        return self.send("suggest", suggest)
