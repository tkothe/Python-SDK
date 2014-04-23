#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]

EasyCollins is the attempt to make collins a little bit more userfriendly
and hides much of the direct calls to the Collins API.


Class Structures
----------------

.. digraph:: objects

    node[shape=none];

    easy[label=<<table cellspacing="0" border="0" cellborder="1">
        <tr><td colspan="2">EasyCollins</td></tr>
        <tr><td>categories()</td><td></td></tr>
        <tr><td>categoryById()</td><td></td></tr>
        <tr><td>categoryByName()</td><td></td></tr>
        <tr><td>facetgroupById()</td><td></td></tr>
        <tr><td>productsById()</td><td></td></tr>
        <tr><td>productsByEAN()</td><td></td></tr>
    </table>>];

    category[label=<<table cellspacing="0" border="0" cellborder="1">
        <tr><td colspan="2">Category</td></tr>
        <tr><td>id</td><td></td></tr>
        <tr><td>name</td><td></td></tr>
        <tr><td>active</td><td></td></tr>
        <tr><td>parent</td><td></td></tr>
        <tr><td>position</td><td></td></tr>
        <tr><td port="categories">sub_categories</td><td></td></tr>
        <tr><td>treeiter()</td><td></td></tr>
    </table>>];

    facetgroup[label=<<table cellspacing="0" border="0" cellborder="1">
        <tr><td colspan="2">FacetGroup</td></tr>
        <tr><td>id</td><td></td></tr>
        <tr><td>name</td><td></td></tr>
        <tr><td port="facets">facets</td><td></td></tr>
    </table>>];

    facet[label=<<table cellspacing="0" border="0" cellborder="1">
        <tr><td colspan="2">Facet</td></tr>
        <tr><td>id</td><td></td></tr>
        <tr><td>facet_id</td><td></td></tr>
        <tr><td>group_name</td><td></td></tr>
        <tr><td>name</td><td></td></tr>
        <tr><td>value</td><td>if not group: brand</td></tr>
        <tr><td>options</td><td> if group: brand</td></tr>
    </table>>];

    image[label=<<table cellspacing="0" border="0" cellborder="1">
        <tr><td colspan="2">Image</td></tr>
        <tr><td>hash</td><td></td></tr>
        <tr><td>ext</td><td></td></tr>
        <tr><td>mime</td><td></td></tr>
        <tr><td>size</td><td></td></tr>
        <tr><td>image</td><td>"width": 672, "height": 960</td></tr>
        <tr><td>url()</td><td></td></tr>
    </table>>];


.. digraph:: classes2

    node[shape=none];

    product[label=<<table cellspacing="0" border="0" cellborder="1">
        <tr><td colspan="2">Product</td></tr>
        <tr><td port="category">categories</td><td></td></tr>
        <tr><td port="default_variant">default_variant</td><td></td></tr>
        <tr><td port="id">id</td><td></td></tr>
        <tr><td port="image">default_image</td><td></td></tr>
        <tr><td port="variants">variants</td><td></td></tr>
        <tr><td>active</td><td></td></tr>
        <tr><td>description_long</td><td></td></tr>
        <tr><td>description_short</td><td></td></tr>
        <tr><td>max_price</td><td></td></tr>
        <tr><td>min_price</td><td></td></tr>
        <tr><td>name</td><td></td></tr>
        <tr><td>sale</td><td></td></tr>
        <tr><td>styles</td><td></td></tr>
        <tr><td>url()</td><td></td></tr>
    </table>>];

    variant[label=<<table cellspacing="0" border="0" cellborder="1">
        <tr><td colspan="2">Variant</td></tr>
        <tr><td>id</td><td></td></tr>
        <tr><td>attributes</td><td></td></tr>
        <tr><td>images</td><td></td></tr>
        <tr><td>additional_info</td><td></td></tr>
        <tr><td>created_date</td><td></td></tr>
        <tr><td>default</td><td></td></tr>
        <tr><td>ean</td><td></td></tr>
        <tr><td>first_active_date</td><td></td></tr>
        <tr><td>first_sale_date</td><td></td></tr>
        <tr><td>old_price</td><td></td></tr>
        <tr><td>price</td><td></td></tr>
        <tr><td>quantity</td><td></td></tr>
        <tr><td>retail_price</td><td></td></tr>
        <tr><td>updated_date</td><td></td></tr>
        <tr><td>live()</td><td></td></tr>
    </table>>];

"""
from . import Collins, Constants, CollinsException


class EasyNode(object):
    """A simple wrapper around a dict object."""

    def __init__(self, easy, obj):
        self.easy = easy
        self.obj = obj

        if "error_message" in obj or "error_code" in obj:
            raise CollinsException("{} {}".format(obj["error_code"], obj["error_message"]))

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

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class FacetGroup(object):
    def __init__(self, easy, fid, name, facets):
        self.id = fid
        self.name = name
        self.facets = facets

    def __getitem__(self, idx):
        return self.facets[idx]

    def __iter__(self):
        for facet in self.facets.values():
            yield facet

    def __len__(self):
        return len(self.facets)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Image(EasyNode):
    def __init__(self, easy, obj):
        super(Image, self).__init__(easy, obj)

    def url(self):
        return self.easy.collins.config.image_url.format(self.hash)

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
            self.__data[facets.name] = [facets[f] for f in value]
            self.__data[facets.id] = self.__data[facets.name]

    def keys(self):
        return self.__data.keys()

    def __getitem__(self, idx):
        if idx in self.__data:
            return self.__data[idx]
        else:
            return []


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

    @property
    def live(self):
        return self.easy.collins.livevariant([self.id])


class Product(EasyNode):
    def __init__(self, easy, obj):
        super(Product, self).__init__(easy, obj)

        self.__variants = None
        self.__categories = None
        self.__short_description = None
        self.__long_description = None
        self.__default_image = None
        self.__default_variant = None

    def url(self):
        """
        Returns the url to the product in the mary+paul shop.
        """
        slug = self.name.strip().replace(" ", "-") + "-" + str(self.id)
        return self.easy.collins.config.product_url.format(slug)

    @property
    def categories(self):
        """
        :returns: A list of :py:class:`collins.easy.Category`.
        """
        if self.__categories is None:
            catname = "categories.{}".format(self.easy.config.app_id)

            if catname not in self.obj:
                data = self.easy.collins.products(ids=[self.id],
                                                fields=[Constants.PRODUCT_FIELD_CATEGORIES])
                self.obj.update(data["ids"][str(self.id)])

            self.__categories = [[self.easy.categoryById(cid) for cid in path]
                                for path in self.obj[catname]]

        return self.__categories

    @property
    def variants(self):
        """
        :returns: A list of :py:class:`collins.easy.Variant`.
        """
        if self.__variants is None:
            if "variants" not in self.obj:
                data = self.easy.collins.products(ids=[self.id],
                                                fields=[Constants.PRODUCT_FIELD_VARIANTS])
                self.obj.update(data["ids"][str(self.id)])

            self.__variants = [Variant(self.easy, v) for v in self.obj["variants"]]

        return self.__variants

    @property
    def default_image(self):
        if self.__default_image is None:
            if "default_image" not in self.obj:
                data = self.easy.collins.products(ids=[self.id],
                                                fields=[Constants.PRODUCT_FIELD_DEFAULT_IMAGE])
                self.obj.update(data["ids"][str(self.id)])

            self.__default_image = Image(self.easy, self.obj["default_image"])

        return self.__default_image

    @property
    def default_variant(self):
        if self.__default_variant is None:
            if "default_variant" not in self.obj:
                data = self.easy.collins.products(ids=[self.id],
                                                fields=[Constants.PRODUCT_FIELD_DEFAULT_VARIANT])
                self.obj.update(data["ids"][str(self.id)])

            self.__default_variant = Variant(self.easy, self.obj["default_variant"])

        return self.__default_variant

    def __getattr__(self, name):
        if name not in self.obj:
            data = self.easy.collins.products(ids=[self.id],
                                            fields=[
                                                    Constants.PRODUCT_FIELD_DESCRIPTION_SHORT,
                                                    Constants.PRODUCT_FIELD_DESCRIPTION_LONG,
                                                    Constants.PRODUCT_FIELD_SALE])
            self.obj.update(data["ids"][str(self.id)])

        return self.obj[name]


# class SearchFilter(object):
#     def __init__(self):
#         self.categories = set()
#         self.facets = {}
#         self.prices_from = None
#         self.prices_to = None
#         self.searchword = None
#         self.sale = None

#     def build(self):
#         f = {"sale": self.sale}

#         if len(self.categories) > 0:
#             f["categories"] = [c.id for c in self.categories]

#         if self.searchword is not None:
#             f["searchword"] = self.searchword

#         if len(self.facets) > 0:
#             pass

#         if self.prices_from is not None and self.prices_to is not None:
#             f["prices"] = {
#                 "from": self.prices_from,
#                 "to": self.prices_to
#             }

#         return f


# class SearchResult(object):
#     def __init__(self):
#         self.sale = False
#         self.price = False
#         self.facets = None
#         self.limit = None
#         self.offset = None
#         self.categories = None

#     def build(self):
#         s = {"sale": self.sale, "price": self.price}

#         if self.limit is not None:
#             s["limit"] = self.limit

#         if self.offset is not None:
#             s["offset"] = self.offset

#         if self.categories is not None:
#             s["categories"] = self.categories

#         if self.facets is not None:
#             s["facets"] = self.facets

#         return s


class ResultProducts(object):
    def __init__(self, search):
        self.search = search
        self.buffer = [None] * search.count

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            self.search.gather(idx.start, idx.stop-idx.start)

            return [self.buffer[i] for i in xrange(idx.start, idx.stop, idx.step)]

        if self.buffer[idx] is None:
            self.search.gather(idx, 1)

        return self.buffer[idx]

    def __len__(self):
        return self.search.count

    def __iter__(self):
        step = 100
        for i in xrange(0, self.search.count):
            if self.buffer[i] is None:
                self.search.gather(i, step)

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

        self.obj = self.easy.collins.productsearch(self.sessionid,
                                                   filter=self.filter,
                                                   result=self.result)

        self.count = self.obj["product_count"]

        self.products = ResultProducts(self)

        if "categories" in self.obj["facets"]:
            for el in self.obj["factes"]["categories"]:
                cat = self.search.easy.categoryById(el["term"])
                self.categories[cat] = el["count"]


    def gather(self, offset, limit):
        response = self.easy.collins.productsearch(self.sessionid,
                                                   filter=self.filter,
                                                   result={"offset":offset,
                                                            "limit": limit})

        for i, p in enumerate(response["products"]):
            if p["id"] in self.easy.product_cach:
                product = self.easy.product_cach[p["id"]]
            else:
                product = Product(self.easy, p)

            self.easy.product_cach[product.id] = product
            self.products.buffer[i+offset] = product


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

        self.__simple_colors = None

        self.__baskets = {}
        self.product_cach = {}

        # if self.config.cache is not None:
        #     try:
        #         self.__bucket = pylibmc.Client(self.config.cache,
        #                                        binary=True,
        #                                        behaviors={"tcp_nodelay": True, "ketama": True})
        #     except:
        #         self.collins.log.exception('')

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

    def getSimpleColors(self):
        """
        Returns an array of facet colors which are a simple selection out
        of the hugh possebilities.
        """
        if self.__facet_map is None:
            self.__build_facets()

        if self.__simple_colors is None:
            colors = self.facetgroupById('color')
            self.__simple_colors = []
            for fid in [570, 168, 67, 247, 48, 14, 18, 204, 30, 1, 579, 15, 12,
                        11, 55, 580, 9, 333, 646]:
                self.__simple_colors.append(colors[fid])

        return self.__simple_colors

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

    def productsById(self, pids):
        """
        Gets a products by its id.

        :param list pids: A list of product ids.
        :returns: A list of :py:class:`collins.easy.Product` instance.
        """
        spid = [str(pid) for pid in pids if pid not in self.product_cach]

        products = [self.product_cach[pid] for pid in pids if pid in self.product_cach]

        if len(spid) > 0:

            response = self.collins.products(ids=pids, fields=[Constants.PRODUCT_FIELD_SALE])

            new = [Product(self, p) for p in response["ids"].values()]

            for n in new:
                self.product_cach[n.id] = n

            products += new

        return products

    def productsByEAN(self, eans):
        """
        Gets products by its ean code.

        :param int ean: Product ean.
        :returns: A :py:class:`collins.easy.Product` instance.
        """
        response = self.collins.producteans(eans=eans)

        return [Product(self, p) for p in response]

    def search(self, sessionid, filter=None, result=None):
        """
        Creates a new :py:class:`collins.easy.Search` instance.

        .. note:: See :py:func:`collins.Collins.productsearch`.

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
