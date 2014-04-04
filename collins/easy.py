#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon => [arne_simon@gmx.de]

EasyCollins is the attempt to make collins a little bit more userfriendly
and hides much of the direct calls to the Collins API.

Example
-------

.. code-block:: python

    from collins import JSONConfig
    from collins.easy import EasyCollins

    config = JSONConfig('slicedice-config.json')
    easy = EasyCollins(config)
    product = easy.productById(227838)

    for c in easy.categories():
        print '---', c.name, '---'
        for sub in c:
            print sub.name
"""
from collins import Collins, Constants, CollinsException


class EasyNode(object):
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
        def browse(node):
            yield node

            for sub in node.sub_categories:
                for child in browse(sub):
                    yield child

        return browse(self)

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


class SearchResult(object):
    def __init__(self, easy):
        self.easy = easy


class Basket(object):
    """
    :param easy: The EasyCollins instance.
    :param sessionid: The session id the basket is associated with.
    """
    def __init__(self, easy, sessionid):
        self.easy = easy
        self.sessionid = sessionid

        self.__variants = {}

    def __getindex__(self, idx):
        if issubclass(idx, Variant):
            return self.__variants[idx]
        else:
            raise CollinsException("accepts only Variant instances as key")

    def __setindex__(self, idx, val):
        if issubclass(idx, Variant):
            self.__variants[idx] = val
        else:
            raise CollinsException("accepts only Variant instances as key")

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

        self.__facet_map = None
        self.__facet_groups = {}

        self.__baskets = {}

        try:
            import pylibmc
            self.__cash = pylibmc.Client(["127.0.0.1"], binary=True,
                            behaviors={"tcp_nodelay": True, "ketama": True})

            # we do this as a check to see if the server is realy there
            self.__cash["dummy"]
            del self.__cash["dummy"]
        except:
            # dirty little fallback }:->
            self.collins.log.exception('')
            self.collins.log.warn('using caching fallback')
            self.__cash = {}

    def __build_categories(self):
        self.collins.log.info('cache category tree')
        tree = self.collins.categorytree()

        def build(n):
            c = Category(self, n)
            self.__category_ids[c.id] = c
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

    def __create_product(self, obj):
        p = Product(self, obj)

        for variant in p.variants:
            cachkey = "ean_{}".format(variant.ean)
            self.__cash[cachkey] = p

        self.__cash[str(p.id)] = p

        return p

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
        if spid in self.__cash:
            return self.__cash[spid]
        else:
            response = self.collins.products(ids=[pid],
                                             fields=[Constants.PRODUCT_FIELD_VARIANTS])

            p = self.__create_product(response["ids"][spid])

            return p

    def productByEAN(self, ean):
        """
        Gets a product by its ean code.

        :param int ean: Product ean.
        :returns: A :py:class:`collins.easy.Product` instance.
        """
        cachkey = "ean_{}".format(ean)

        if cachkey in self.__cash:
            return self.__cash[cachkey]
        else:
            response = self.collins.producteans(eans=[ean],
                                         fields=[Constants.PRODUCT_FIELD_VARIANTS])

            p = self.__create_product(self, response["eans"][0])

            return p

    def search(self, sessionid):
        """
        .. todo:: Not implementes yet :(
        """
        pass

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
                spid = str(p["id"])

                if spid in self.__cash:
                    products.append(self.__cash[spid])
                else:
                    pobj = self.__create_product(p)
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
