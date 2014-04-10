#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]

EasyCollins is the attempt to make collins a little bit more userfriendly
and hides much of the direct calls to the Collins API.

"""
from . import Collins, Constants, CollinsException


class EasyNode(object):
    """A simple wrapper around a dict object."""

    def __init__(self, easy, obj):
        self.easy = easy
        self.obj = obj

    def __getattr__(self, name):
        return self.obj[name]

    def __getitem__(self, idx):
        return self.obj[idx]


class Category(EasyNode):
    def __init__(self, easy, obj):
        super(Category, self).__init__(easy, obj)

        self.sub_categories = []

    def treeiter(self):
        def browse(level, node):
            yield level, node

            nextlevel = level + 1

            for sub in node.sub_categories:
                for child in browse(nextlevel, sub):
                    yield child

        return browse(0, self)

    def __iter__(self):
        for sub in self.sub_categories:
            yield sub


class FacetGroup(object):
    def __init__(self, easy, fid, name, facets):
        self.id = fid
        self.name = name
        self.facets = facets

    def __getitem__(self, idx):
        return self.facets[idx]

    def __iter__(self):
        for name, facet in self.facets.items():
            yield name, facet

    def __len__(self):
        return len(self.facets)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Image(EasyNode):
    def __init__(self, easy, obj):
        super(Image, self).__init__(easy, obj)

    def __str__(self):
        return self.easy.collins.config.image_url.format(self.hash)

    def __unicode__(self):
        return self.easy.collins.config.image_url.format(self.hash)


class VariantAttributes(object):
    def __init__(self, easy, obj):
        self.obj = obj

        prefixlen = len("attributes_")
        self.__data = {}

        for name, value in obj.items():
            grpid = int(name[prefixlen:])
            facets = easy.facetgroupById(grpid)
            self.__data[facets] = [facets[f] for f in value]

    def keys(self):
        return self.__data.keys()


class Variant(EasyNode):
    def __init__(self, easy, obj):
        super(Variant, self).__init__(easy, obj)

        self.__images = [Image(easy, i) for i in obj["images"]]
        self.__attributes = VariantAttributes(easy, obj["attributes"])

    @property
    def images(self):
        return self.__images

    @property
    def attributes(self):
        return self.__attributes


class Product(EasyNode):
    def __init__(self, easy, obj):
        super(Product, self).__init__(easy, obj)

        if "variants" in obj:
            self.__variants = [Variant(easy, v) for v in obj["variants"]]
        else:
            self.__variants = None

    @property
    def variants(self):
        if self.__variants is None:
            response = self.easy.collins.products(ids=[self.id],
                                             fields=[Constants.PRODUCT_FIELD_VARIANTS])

            self.__variants = [Variant(self.easy, v)
                                for v in response["ids"][str(self.id)]["variants"]]
        return self.__variants


class SearchFilter(object):
    def __init__(self):
        self.categories = set()
        self.facets = {}
        self.prices_from = None
        self.prices_to = None
        self.searchword = None
        self.sale = None

    def build(self):
        f = {"sale": self.sale}

        if len(self.categories) > 0:
            f["categories"] = [c.id for c in self.categories]

        if self.searchword is not None:
            f["searchword"] = self.searchword

        if len(self.facets) > 0:
            pass

        if self.prices_from is not None and self.prices_to is not None:
            f["prices"] = {
                "from": self.prices_from,
                "to": self.prices_to
            }

        return f


class SearchResult(object):
    def __init__(self):
        self.sale = False
        self.price = False
        self.facets = None
        self.limit = None
        self.offset = None
        self.categories = None

    def build(self):
        s = {"sale": self.sale, "price": self.price}

        if self.limit is not None:
            s["limit"] = self.limit

        if self.offset is not None:
            s["offset"] = self.offset

        if self.categories is not None:
            s["categories"] = self.categories

        if self.facets is not None:
            s["facets"] = self.facets

        return s


class ResultProducts(object):
    def __init__(self, search):
        self.search = search
        self.buffer = [None] * search.count

    def all(self):
        return self.__buffer

    def __getindex__(self, idx):
        if self.buffer[idx] is not None:
            return self.buffer[idx]
        else:
            self.gather()

    def __iter__(self):
        step = 0
        for i in xrange(self.search.count):
            if self.buffer[i] is None:
                self.search.gather(i, 20)

            yield self.buffer[i]


class Search(object):
    def __init__(self, easy, sessionid, filter=None, result=None):
        self.easy = easy
        self.sessionid = sessionid
        self.filter = filter
        self.categories = {}

        if result is None:
            self.result = {"limit": 0, "offset": 0}
        else:
            self.result = result
            self.result["limit"] = 0
            self.result["offset"] = 0

        response = self.easy.collins.productsearch(self.sessionid,
                                                   filter=self.filter,
                                                   result=self.result)

        self.count = response["product_count"]

        self.products = ResultProducts(self)

        if "categories" in response["facets"]:
            for el in response["factes"]["categories"]:
                cat = self.search.easy.categoryById(el["term"])
                self.categories[cat] = el["count"]


    def gather(self, offset, limit):
        response = self.easy.collins.productsearch(self.sessionid,
                                                   filter=self.filter,
                                                   result={"offset":offset,
                                                            "limit": limit})

        for i, p in enumerate(response["products"]):
            self.products.buffer[i+offset] = Product(self.easy, p)

        return self.products.buffer[offset:offset+limit]


class Basket(object):
    """
    :param easy: The EasyCollins instance.
    :param sessionid: The session id the basket is associated with.
    """
    def __init__(self, easy, sessionid):
        self.easy = easy
        self.sessionid = sessionid

        self.__variants = {}

    def __getitem__(self, idx):
        # self.easy
        return self.__variants[idx]

    def __setitem__(self, idx, val):
        self.__variants[idx] = val

    def __delitem__(self, idx):
        #self.easy.basketadd()
        del self.__variants[idx]

    def order(self):
        """
        Begins to order this basket.
        """
        pass


class EasyCollins(object):
    """
    :param config: A :py:class:`collins.Config` instance.
    """
    def __init__(self, config):
        self.config = config

        self.collins = Collins(self.config)
        self.__categorytree = None
        self.__category_ids = {}
        self.__category_names = {}

        self.__facet_map = None
        self.__facet_groups = {}

        self.__baskets = {}

    def __build_categories(self):
        self.collins.log.info('cache category tree')
        tree = self.collins.categorytree()

        def build(n):
            c = Category(self, n)
            self.__category_ids[c.id] = c
            self.__category_names[c.name] = c
            c.sub_categories = [build(x) for x in n["sub_categories"]]
            return c

        self.__categorytree = [build(node) for node in tree]

    def __build_facets(self):
        self.collins.log.info('cache facets')

        self.__facet_map = {}
        facets = self.collins.facettypes()
        for f in facets:
            response = self.collins.facets([f])["facet"]
            self.__facet_map[response[0]["group_name"]] = f
            self.__facet_map[f] = response[0]["group_name"]

            group = FacetGroup(self, f, response[0]["group_name"],
                               dict(((r["facet_id"], EasyNode(self, r))
                                                for r in response)))

            self.__facet_groups[f] = group

    def basketBySession(self, sessionid):
        """
        Returns a basket for the session id.

        :param sessionid: The session id the basket is associated with.
        :returns: :py:class:`collins.easy.Basket`
        """
        if sessionid in self.__baskets:
            return self.__baskets[sessionid]
        else:
            b = Basket(self, sessionid)

            self.__baskets[sessionid] = b

            return b

    def categories(self):
        """
        Returns the category tree.

        :returns: A list of :py:class:`collins.easy.Category`.
        """
        if self.__categorytree is None:
            self.__build_categories()

        return self.__categorytree

    def categoryById(self, cid):
        """
        Returns the category with the given id.

        :param cid: The id of the category to get.
        :returns: A :py:class:`collins.easy.Category` instance.
        """
        if self.__categorytree is None:
            self.__build_categories()

        return self.__category_ids[cid]

    def categoryByName(self, name):
        """
        Returns the category with the given name.

        .. note:: If there are more than one category with the same name.
                    The last inserted category will be returned.

        :param str name: The name of the category.
        :returns: A :py:class:`collins.easy.Category` instance.
        """
        if self.__categorytree is None:
            self.__build_categories()

        return self.__category_names[name]

    def facetgroupById(self, facet_group):
        """
        Returns all facets of a group.

        :param facet_group: The id or name of the facet group.
        :returns: A :py:class:`collins.easy.FacetGroup` instance.
        """
        if self.__facet_map is None:
            self.__build_facets()

        if isinstance(facet_group, (str, unicode)):
            facet_group = self.__facet_map[facet_group]

        return self.__facet_groups[facet_group]

    def productById(self, pid):
        """
        Gets a product by its id.

        :param int pid: Product id.
        :returns: A :py:class:`collins.easy.Product` instance.
        """
        spid = str(pid)
        response = self.collins.products(ids=[pid],
                                         fields=[Constants.PRODUCT_FIELD_VARIANTS])

        p = Product(self, response["ids"][spid])

        return p

    def productByEAN(self, ean):
        """
        Gets a product by its ean code.

        :param int ean: Product ean.
        :returns: A :py:class:`collins.easy.Product` instance.
        """
        response = self.collins.producteans(eans=[ean],
                                     fields=[Constants.PRODUCT_FIELD_VARIANTS])

        p = Product(self, response[0])

        return p

    def search(self, sessionid, filter=None, result=None):
        """
        Creates a new :py:class:`collins.easy.Search` instance.

        :param sessionid: The user session id.
        :returns: A :py:class:`collins.easy.Search` instance.
        """
        return Search(self, sessionid, filter, result)

    def autocomplete(self, searchword, types=None, limit=None):
        """
        Autocompletes the searchword and looks in the products and/or
        categories for autocompletion possebilities.

        :param str searchword: The abbriviation.
        :param list types: against which types should be autocompleted.
                            The oprions are :py:class:`collins.Constants.TYPES`
        :param int limit: the amount of items returned per selected type
        :returns: A tuple of two list. First one are the products and the second
                 are the categories.

        .. rubric:: Example

        .. code-block:: python

            >>> products, categories = easy.autocomplete("sho")
        """
        result = self.collins.autocomplete(searchword,
                                           types=types,
                                           limit=limit)

        products = []
        if types is None or Constants.TYPE_PRODUCTS in types:
            for p in result["products"]:
                pobj = Product(self, p)
                products.append(pobj)

        categories = []
        if types is None or Constants.TYPE_CATEGORIES in types:
            if self.__categorytree is None:
                self.__build_categories()

            for c in result["categories"]:
                scid = c["id"]

                if scid in self.__category_ids:
                    categories.append(self.__category_ids)
                else:
                    raise CollinsException("unknown category {}".format(scid))

        return products, categories

    def suggest(self, searchword, categories=None, limit=None):
        """
        Suggest additional words to the provided searchword.

        :param str searchword: A search string to suggest items for.
        :param list categories: A list of :py:class:`collins.easy.Category`.
        :param int limit: The maximum amount of results.
        :returns: A list of strings.
        """
        if categories is not None:
            categoriescast = [c.id for c in categories]
        else:
            categoriescast = None

        result = self.collins.suggest(searchword,
                                      categories=categoriescast,
                                      limit=limit)
        return result
