#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon => email::[arne_simon@gmx.de]

This module provieds two wrappers around the Collins-Shop-API.

* A thin python wrapper which takes Python dict's and list's and returns the
  result as the same.
* EasyCollins, which is a more convient layer of abstraction of the API as an
  object herachie which caches results and query results if there are needed.
"""
import json
import logging
import logging.config
import logging.handlers
import urllib2


COLLINS_VERSION = "1.1"
"""The version of the collins api which is supported."""

VERSION = "0.0"
"""Version of the python shop SDK."""

AUTHORS = [
    "Arne Simon => email::[arne_simon@gmx.de]"
]


class CollinsException(Exception):
    """An exception in the collins module."""
    pass


class Constants(object):
    """
    Some contsants which are blatantly copied from the php-sdk.

    .. attention::
        The following constants are **NOT** in the PHP-SDK:
            * FACET_CHANNEL
            * FACET_CARE_SYMBOL
            * FACET_CLOTHING_HATS_US
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
    # not in the PHP-SDK o.O
    FACET_CHANNEL = 211
    FACET_CARE_SYMBOL = 247
    FACET_CLOTHING_HATS_US = 231

    FACETS = set([FACET_BRAND , FACET_CLOTHING_MEN_BELTS_CM , FACET_CLOTHING_MEN_DE , FACET_CLOTHING_MEN_INCH ,
                 FACET_CLOTHING_UNISEX_INCH , FACET_CLOTHING_UNISEX_INT , FACET_CLOTHING_UNISEX_ONESIZE ,
                 FACET_CLOTHING_WOMEN_BELTS_CM , FACET_CLOTHING_WOMEN_DE , FACET_CLOTHING_WOMEN_INCH , FACET_COLOR ,
                 FACET_CUPSIZE , FACET_DIMENSION3 , FACET_GENDERAGE , FACET_LENGTH , FACET_SHOES_UNISEX_ADIDAS_EUR ,
                 FACET_SHOES_UNISEX_EUR , FACET_SIZE , FACET_SIZE_CODE , FACET_SIZE_RUN])

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

    API_ENVIRONMENT_STAGE = "stage"
    API_ENVIRONMENT_LIVE = "live"


class Config(object):
    """
    The configuration of a collins api connection.

    A config class has to have the following readable attributes:

    - entry_point_url:
        The url for collins.
    - app_id
        The application id.
    - app_password
        The password for the corresponding application id.
    - agent
        The name of the browser agent to fake.
    - authorization
        The authorization header
    - image_url
        A string as template for the image urls.
        As example http://cdn.mary-paul.de/product_images/{path}/{id}_{width}_{height}{extension}.
    - logging
        A dictonary for logging.config.dictConfig.

    :param str filename: The path to a JSON file which holds the configuration.
    """
    def __init__(self, filename):
        with open(filename) as cfgfile:
            self.data = json.load(cfgfile)

        logging.config.dictConfig(self.data["logging"])

    def __getattr__(self, name):
        return self.data[name]

    def imageurl(self, path, productid, width, height, extension):
        """
        Returns the url for a image.

        :param path: Part of the image path.
        :param productid:
        :param width: Width of the image.
        :param height: Height of the image.
        :param extension: The image extension. For example *'.jpg'*
        """
        return self.data["image_url"].format(path=path, id=productid,
                                             width=width, height=height,
                                             extension=extension)



def check_sessionid(sessionid):
    """
    .. attention::
        We copied it from the php-sdk.
        collins seems to want have the session-id a minimum length of five
        characters. This is not tested or validated.
    """
    if len(sessionid) < 5:
        raise CollinsException("The session id must have at least 5 characters")


class Collins(object):
    """
    An interface to the Collins API.

    This is thin warper around the Collins API.
    All functions return the JSON responses as Python List and Dictonarys.

    :param config: A Config instance or a file name to a JSON config file.
    """

    def __init__(self, config):
        if isinstance(config, Config):
            self.config = config
        else:
            self.config = Config(config)

        logname = "python-shop.collins.{}".format(self.config.app_id)
        self.log = logging.getLogger(logname)
        self.log.debug("instantiated")

    def send(self, cmd, obj):
        """
        Sends a Pyhton structure of dict's and list's as raw JSON to collins and
        returns a Python structure of dict's and list's from the JSON answer.

        :param cmd: The name of the command.
        :param obj: A python dict object which contains the request parameters.
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
            result = json.loads(result)[0][cmd]

            if "error_message" in result:
                raise CollinsException(result["error_message"])

            return result

        except urllib2.HTTPError as err:
            message = "{} {} {}".format(err.code, err.reason, err.read())
            self.log.exception(message)
            raise CollinsException(message)
        except urllib2.URLError as err:
            self.log.exception('')
            raise CollinsException(err.reason)

    def autocomplete(self, searchword, limit=None, types=None):
        """
        :param str searchword: The abbriviation.
        :param list categories: against which types should be autocompleted
        :param int limit: the amount of items returned per selected type

        .. attention::
            In the documentation stands **autocomplete** but the real
            Tag is **autocompletion**!
        """
        complete = {"searchword": searchword}

        if limit is not None:
            if limit < 1 or limit > 200:
                raise CollinsException("limit out of range")

            complete["limit"] = limit

        if types is not None:
            if len(set(types) - Constants.TYPES) > 0:
                raise CollinsException("unknown types")

            complete["types"] = types

        return self.send("autocompletion", complete)

    def basketadd(self, sessionid, products):
        """
        The request "basket add" does change the Items available in the basket.
        A set to 0 or less leads to a deletion. Only the variants in the items
        list will be changed. If a variant is changed or added an internal
        availability check is done and error codes are returned.

        :param str sessionid: identification of the basket -> user,
                              user -> basket
        :param list products: is the array for the product variants

        .. rubric:: product variant dict

        +---------+---------------------------------------------------+
        |fieldname|                    meaning                        |
        +=========+===================================================+
        |id       |the product variant id                             |
        +---------+---------------------------------------------------+
        |command  |either add for the + operator (even -1 is possible)|
        |         |or set for a specific quantity.                    |
        |         |If the end amount is <= 0 the product is           |
        |         |removed from basket with an result code.           |
        +---------+---------------------------------------------------+
        |amount   |the amount to add or set                           |
        +---------+---------------------------------------------------+
        """
        check_sessionid(sessionid)

        data = {"session_id": sessionid,
                # "product_variant": [
                #     {"command": "",
                #      "id": 1,
                #      "amount": 1},
                # ]
                "product_variant": products
            }

        return self.send("basket_add", data)

    def basketget(self, sessionid):
        """
        This returns the current basket for a User / Session ID.
        The basket belongs to a specific app id and session id,
        another app can have the same session id.

        :param str sessionid: identification of the basket -> user,
                              user -> basket
        """
        check_sessionid(sessionid)

        return self.send("basket_get", {"session_id": sessionid})

    def category(self, ids):
        """
        You are able to retrieve single categories.

        :param list ids: List of category ids.

        .. rubric:: Example

        .. codeblock:: python

            collins.category([16077])

        .. codeblock:: json

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
            raise CollinsException("to few ids")

        if idscount > 200:
            raise CollinsException("to many ids, maximum is 200")

        return self.send("category", {"ids": ids})

    def categorytree(self, max_depth=None):
        """
        The request category tree returns a tree of categories of a
        specified max depth for your app id.

        :param int max_depth: max depth of your category tree counted from root

        .. rubric:: Example

        .. codeblock:: python

            collins.categorytree()

        .. codeblock:: json

            [
                {
                    "name": "Damen",
                    "parent": null,
                    "sub_categories": [
                        {
                            "name": "Bekleidung",
                            "parent": 16077,
                            "sub_categories": [
                                {
                                    "name": "Oberteile",
                                    "parent": 16078,
                                    "sub_categories": [
                                        {
                                            "name": "Fr\u00fchlingslooks",
                                            "parent": 16079,
                                            "sub_categories": [],
                                            "active": false,
                                            "position": 1,
                                            "id": 23882
                                        },

                ...

            ]
        """
        if max_depth is None:
            cmd ={}
        else:
            if max_depth < 1:
                raise CollinsException("max_depth to small")

            if max_depth > 10:
                raise CollinsException("max_depth to big")

            cmd = {"max_depth": max_depth}

        return self.send("category_tree", cmd)

    def facets(self, group_ids=None, limit=None, offset=None):
        """
        This returns a list of available facet groups or a facets of a group.

        :param list group_ids: get only these group ids, if empty get all
                                group ids which belong to me
        :param int limit: limit the per page items
        :param int offset: offset for paging through the items

        .. rubric:: Example

        .. codeblock:: python

            collins.facets([Constants.FACET_CUPSIZE])

        .. codeblock:: json

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
                raise CollinsException("limit is to small")

            facets["limit"] = limit

        if group_ids is not None:
            facets["group_ids"] = group_ids

        if offset is not None:
            if offset < 0:
                raise CollinsException('offset out of range')

            facets["offset"] = offset

        return self.send("facets", facets)

    def facettypes(self):
        """
        This query returns a list of facet groups available.

        .. rubric:: Example

        .. codeblock:: python

            collins.facettypes()

        .. codeblock:: json

            [0, 2, 1, 6, 172, 206, 173, 194, 175, 204, 5, 189, 180, 231, 187, 190, 211, 181, 247]
        """

        return self.send("facet_types", {})

    def getorder(self, orderid):
        """Through this query you could get a order which was created
            for/through your app. This is limited to a configured
            timeframe and to your app.

        :param int orderid: this is the order id to get info about
        """
        return self.send("get_order", {"order_id": orderid})

    def initiateorder(self, sessionid, sucess_url,
                      cancel_url=None, error_url=None):
        """At this request you initiate a order to a basket.
            This should be done if a user wants to go to the checkout.

        :param str sessionid: identification of the basket -> user,
                              user -> basket (see basket_get, basket_add)
        :param str sucess_url: this is a callback url if the order was
                               successfully created. (see checkout api)
        :param str cancel_url: this is a callback url if the order was
                               canceled. (see checkout api)
        :param str error_url: this is a callback url if the order throwed
                              exceptions (see checkout api)
        """
        check_sessionid(sessionid)

        order = {"session_id": sessionid, "sucess_url": sucess_url}

        if cancel_url is not None:
            order["cancel_url"] = cancel_url

        if error_url is not None:
            order["error_url"] = error_url

        return self.send("initiate_order", order)

    def livevariant(self, ids):
        """This does return the live information about the product variant.
            This is as "live" as possible.
            And could differ vs. a "product search" or "product" query.

        :param list ids: array of product variant id
        """
        idscount = len(ids)

        if idscount < 1:
            raise CollinsException("too few ids")

        if idscount > 200:
            raise CollinsException("too many ids")

        return self.send("live_variant", {"ids": ids})

    def products(self, ids):
        """
        Here you get a detail view of a product or a list of products returned
        by its ids.

        :param list ids: array of product variant id

        .. rubric:: Example

        .. codeblock:: python

            collins.products([227838, 287677])

        **Returns:**

        .. codeblock:: json

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
        idscount = len(ids)

        if idscount < 1:
            raise CollinsException("too few ids")

        if idscount > 200:
            raise CollinsException("too many ids")

        return self.send("products", {"ids": ids})

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
            To get facet types see :py:class:`collins.Constants`

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

        .. codeblock:: python

            # i belive we search shorts now o.O
            collins.productsearch(TEST_SESSION_ID, filter={"categories":[16354]})

        **Returns:**

        .. codeblock:: json

            {
                "product_count": 78,
                "pageHash": "6e63cadb-5505-47b7-b36d-643311292a22",
                "facets": {},
                "products": [
                    {
                        "id": 227838,
                        "name": "Badeshort Herren"
                    },

                    ...
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
        """
        suggest = {"searchword": searchword}

        if categories is not None:
            suggest["categories"] = categories

        if limit is not None:
            if limit < 1 or limit > 200:
                raise CollinsException('The limit has to between 1 and 200.')

            suggest["limit"] = limit

        return self.send("suggest", suggest)


class EasyCollins(object):
    def __init__(self, conf_or_filename):
        if isinstance(conf_or_filename, Config):
            self.config = conf_or_filename
        else:
            self.config = Config(conf_or_filename)

        self.collins = Collins(self.config)

if __name__ == '__main__':
    c = Collins("slicedice-config.json")
    open('dump.json','w').write(json.dumps(c.facets([Constants.FACET_CUPSIZE]), indent=4))
    # open('dump.json','w').write(json.dumps(c.send("styles", {"ids":["m01_233966406"]}), indent=4))