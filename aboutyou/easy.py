#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]

EasyAboutYou is the attempt to make aboutyou a little bit more userfriendly
and hides much of the direct calls to the aboutyou API.


Class Structures
----------------

.. digraph:: objects

    node[shape=none];

    easy[label=<<table cellspacing="0" border="0" cellborder="1">
        <tr><td colspan="2">EasyAboutYou</td></tr>
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
from . import Aboutyou, Constants, AboutYouException
import bz2
import json
import logging


logger = logging.getLogger('aboutyou')


def safe(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception('stuff')
            raise e

    return wrapper


class EasyNode(object):
    """A simple wrapper around a dict object."""

    def __init__(self, easy, obj):
        self.easy = easy
        self.obj = obj

        if "error_message" in obj or "error_code" in obj:
            raise AboutYouException("{} {}".format(obj["error_code"], obj["error_message"]))

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

    def url(self, width=None, height=None):
        url = self.easy.aboutyou.config.image_url.format(self.hash)
        sizes = []

        if width:
            sizes.append('width={}'.format(width))

        if height:
            sizes.append('height={}'.format(height))

        if len(sizes) > 0:
            url += '?' + '&'.join(sizes)

        return url

    def __str__(self):
        return self.easy.aboutyou.config.image_url.format(self.hash)

    def __unicode__(self):
        return self.easy.aboutyou.config.image_url.format(self.hash)


class VariantAttributes(object):
    def __init__(self, easy, obj):
        self.obj = obj
        self.easy = easy

        prefixlen = len("attributes_")
        self.__data = {}

        for name, value in obj.items():
            grpid = int(name[prefixlen:])
            facets = easy.facetgroupById(grpid)

            collection = []
            for f in value:
                g = facets.facets.get(f, None)

                if g is None:
                    g = EasyNode(easy, {'id': facets.id,
                                        'name': 'unknown_{}'.format(f),
                                        'value': 'unknown_{}'.format(f),
                                        'facet_id': f})
                    facets.facets[f] = g

                collection.append(g)

            self.__data[facets.name] = collection
            self.__data[facets.id] = collection

    def keys(self):
        return self.__data.keys()

    def __getitem__(self, idx):
        if idx in self.__data:
            return self.__data[idx]
        else:
            return []


class Variant(EasyNode):
    """
    A variant of a Product.
    """
    def __init__(self, easy, obj):
        super(Variant, self).__init__(easy, obj)

        self.__images = [Image(easy, i) for i in obj["images"]]
        self.__attributes = VariantAttributes(easy, obj["attributes"])

    @property
    def images(self):
        """
        An array of :py:class:`aboutyou.easy.Image`.
        """
        return self.__images

    @property
    def attributes(self):
        """
        The attributes aka facets of this product variant.
        """
        return self.__attributes

    @property
    def live(self):
        """
        The live data to this variant.
        """
        return self.easy.aboutyou.livevariant([self.id])


class Product(EasyNode):
    """
    A product with its variants.

    .. note::

        The Product class is an extensive user of the auto_fetch feature.
        If enabled in the configuration, when accessing a field which data
        is not present, for example the variants, then the variants will be
        automaticly request.
    """
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
        Returns the url to the product in the shop.
        """
        slug = self.name.strip().replace(" ", "-") + "-" + str(self.id)
        return self.easy.aboutyou.config.product_url.format(slug)

    @property
    def categories(self):
        """
        :returns: A list of :py:class:`aboutyou.easy.Category`.
        """
        if self.__categories is None:
            catname = "categories.{}".format(self.easy.config.app_id)

            if catname not in self.obj and self.easy.config.auto_fetch:
                self.easy.aboutyou.log.debug('update categories from product %s', self.obj['id'])
                data = self.easy.aboutyou.products(ids=[self.id],
                                                fields=[Constants.PRODUCT_FIELD_CATEGORIES])
                self.obj.update(data["ids"][str(self.id)])

            self.__categories = [[self.easy.categoryById(cid) for cid in path]
                                for path in self.obj[catname]]

        return self.__categories

    @property
    def variants(self):
        """
        :returns: A list of :py:class:`aboutyou.easy.Variant`.
        """
        if self.__variants is None:

            if "variants" not in self.obj and self.easy.config.auto_fetch:
                self.easy.aboutyou.log.debug('update variants from product %s', self.obj['id'])
                data = self.easy.aboutyou.products(ids=[self.id],
                                                fields=[Constants.PRODUCT_FIELD_VARIANTS])
                self.obj.update(data["ids"][str(self.id)])


            self.__variants = [Variant(self.easy, v) for v in self.obj["variants"]]

        return self.__variants

    @property
    def default_image(self):
        """
        The default image of this product.
        :returns: :py:class:`aboutyou.easy.Image`
        """
        if self.__default_image is None:
            if "default_image" not in self.obj and self.easy.config.auto_fetch:
                self.easy.aboutyou.log.debug('update default_image from product %s', self.obj['id'])
                data = self.easy.aboutyou.products(ids=[self.id],
                                                fields=[Constants.PRODUCT_FIELD_DEFAULT_IMAGE])
                self.obj.update(data["ids"][str(self.id)])

            self.__default_image = Image(self.easy, self.obj["default_image"])

        return self.__default_image

    @property
    def default_variant(self):
        if self.__default_variant is None:
            if "default_variant" not in self.obj and self.easy.config.auto_fetch:
                self.easy.aboutyou.log.debug('update default_variant from product %s', self.obj['id'])
                data = self.easy.aboutyou.products(ids=[self.id],
                                                fields=[Constants.PRODUCT_FIELD_DEFAULT_VARIANT])
                self.obj.update(data["ids"][str(self.id)])

            self.__default_variant = Variant(self.easy, self.obj["default_variant"])

        return self.__default_variant

    def __getattr__(self, name):
        if name not in self.obj and self.easy.config.auto_fetch:
            self.easy.aboutyou.log.debug('update %s from product %s', name, self.obj['id'])
            data = self.easy.aboutyou.products(ids=[self.id],
                                            fields=[
                                                    Constants.PRODUCT_FIELD_DESCRIPTION_SHORT,
                                                    Constants.PRODUCT_FIELD_DESCRIPTION_LONG,
                                                    Constants.PRODUCT_FIELD_SALE])
            self.obj.update(data["ids"][str(self.id)])

        return self.obj[name]


class SearchException(Exception):
    """
    An exception thrown by productsById.

    :param msg: An error message
    :param found: The products with error.
    :param withError: The products with error.
    """
    def __init__(self, msg, found, withError):
        super(type(self), self).__init__(msg)
        self.found = found
        self.withError = withError


class ResultProducts(object):
    def __init__(self, search):
        self.search = search
        self.buffer = [None] * search.count

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            start = idx.start
            if start is None:
                start = 0

            stop = idx.stop
            stop = min(stop, self.search.count)

            step = idx.step
            if step is None:
                step = 1

            count = stop-start
            pos = start
            for i in xrange(count/200):
                self.search.gather(pos, 200)
                pos += 200

            if count%200 != 0:
                self.search.gather(pos, 200)

            return [self.buffer[i] for i in xrange(start, stop, step)]

        if self.buffer[idx] is None:
            self.search.gather(idx, 1)

        return self.buffer[idx]

    def __len__(self):
        return self.search.count

    def __iter__(self):
        step = 200
        for i in xrange(0, self.search.count):
            if self.buffer[i] is None:
                self.search.gather(i, step)

            yield self.buffer[i]


class Search(object):
    """
    Representing an initiated search.
    """
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

        self.obj = self.easy.aboutyou.productsearch(self.sessionid,
                                                   filter=self.filter,
                                                   result=self.result)

        self.count = self.obj["product_count"]

        self.products = ResultProducts(self)

        if "categories" in self.obj["facets"]:
            for el in self.obj["factes"]["categories"]:
                cat = self.search.easy.categoryById(el["term"])
                self.categories[cat] = el["count"]


    def gather(self, offset, limit):
        self.result['offset'] = offset
        self.result['limit'] = limit

        self.easy.aboutyou.log.debug('gather %s %s %s',
                                     self.sessionid, self.filter, self.result)

        response = self.easy.aboutyou.productsearch(self.sessionid,
                                                   filter=self.filter,
                                                   result=self.result)

        for i, p in enumerate(response["products"]):
            product = None

            if self.easy.cache is not None:
                product = self.easy.cache.get(str(p["id"]))

            if product is None:
                product = Product(self.easy, p)

                if self.easy.cache is not None:
                    self.easy.cache[str(product.id)] = product

            self.products.buffer[i+offset] = product


class BasketException(Exception):
    def __init__(self, msg, fine, withError):
        super(type(self), self).__init__(msg)

        self.fine = fine
        self.withError = withError


class Basket(object):
    """
    :param easy: The EasyAboutYou instance.
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

    def keys(self):
        return self.__variants.keys()

    def values(self):
        return self.__variants.values()

    def items(self):
        return self.__variants.items()

    def order(self, success_url, cancel_url=None, error_url=None):
        """
        Begins to order this basket.

        :param str sucess_url: this is a callback url if the order was successfully created.
        :param str cancel_url: this is a callback url if the order was canceled.
        :param str error_url: this is a callback url if the order throwed exceptions.
        :returns: The url to the shop.
        """
        variants = []

        for variant, count in self.__variants.items():
            pass

        response = self.easy.aboutyou.basketset(self.sessionid, variants)

        return self.easy.aboutyou.order(self.sessionid, sucess_url,
                                       cancel_url, error_url)


class EasyAboutYou(object):
    """
    An abstraction layer around the thin aboutyou api.

    :param config: A :py:class:`aboutyou.Config` instance.
    """
    def __init__(self, config):
        self.config = config

        self.aboutyou = Aboutyou(self.config)
        self.__categorytree = None
        self.__category_ids = {}
        self.__category_names = {}

        self.__facet_map = None
        self.__facet_groups = []

        self.__simple_colors = None

        self.__baskets = {}

        self.cache = None

        if self.config.cache is not None and len(self.config.cache) > 0:
            try:
                import pylibmc

                self.cache = pylibmc.Client(self.config.cache['hosts'],
                                            binary=True,
                                            behaviors={"tcp_nodelay": True, "ketama": True})
                self.cache.get('TEST_TOKEN')
                self.aboutyou.log.info('use memcached via pylibmc')
            except:
                self.cache = None
                self.aboutyou.log.exception('')

    def __build_categories(self):
        tree = None

        if self.cache is not None:
            tree = self.cache.get('categorytree')
            tree = json.loads(bz2.decompress(tree))
            self.aboutyou.log.info('cached category tree')

        if tree is None:
            self.aboutyou.log.info('get category tree from aboutyou')
            tree = self.aboutyou.categorytree()

            if self.cache is not None:
                self.cache.set('categorytree', bz2.compress(json.dumps(tree)),
                                time=self.config.cache['timeout'])

        def build(n):
            c = Category(self, n)
            self.__category_ids[c.id] = c
            self.__category_names[c.name] = c
            c.sub_categories = [build(x) for x in n["sub_categories"]]
            return c

        self.__categorytree = [build(node) for node in tree]

    def __build_facets(self):
        facets = None

        if self.cache is not None:
            facets = self.cache.get('facettypes')
            response = self.cache.get('facets')
            facets = json.loads(bz2.decompress(facets))
            response = json.loads(bz2.decompress(response))
            self.aboutyou.log.info('cached facets')

        if facets is None:
            facets = self.aboutyou.facettypes()
            response = self.aboutyou.facets(facets)["facet"]

            if self.cache is not None:
                self.cache.set('facettypes', bz2.compress(json.dumps(facets)),
                               self.config.cache['timeout'])
                self.cache.set('facets', bz2.compress(json.dumps(response)),
                               self.config.cache['timeout'])

        self.__facet_map = {}
        for facet in response:
            f = EasyNode(self, facet)
            group = self.__facet_map.get(f.group_name)
            if group is None:
                group = FacetGroup(self, f.id, f.group_name, {})
                self.__facet_map[group.name] = group
                self.__facet_map[group.id] = group
                self.__facet_groups.append(group)

            group.facets[f.facet_id] = f


    def basket(self, sessionid):
        """
        Returns a basket for the session id.

        :param sessionid: The session id the basket is associated with.
        :returns: :py:class:`aboutyou.easy.Basket`
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

        :returns: A list of :py:class:`aboutyou.easy.Category`.
        """
        if self.__categorytree is None:
            self.__build_categories()

        return self.__categorytree


    def categoryById(self, cid):
        """
        Returns the category with the given id.

        :param cid: The id of the category to get.
        :returns: A :py:class:`aboutyou.easy.Category` instance.
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
            self.aboutyou.log.info('build simple colors')

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
        :returns: A :py:class:`aboutyou.easy.Category` instance.
        """
        if self.__categorytree is None:
            self.__build_categories()

        return self.__category_names[name]


    def facetGroups(self):
        """
        :Retuns: A set of all known facet groups.
        """
        if self.__facet_map is None:
            self.__build_facets()

        return self.__facet_groups


    def facetgroupById(self, facet_group):
        """
        Returns all facets of a group.

        :param facet_group: The id or name of the facet group.
        :returns: A :py:class:`aboutyou.easy.FacetGroup` instance.
        """
        if self.__facet_map is None:
            self.__build_facets()

        return self.__facet_map[facet_group]


    def productsById(self, pids, fields=['sale', 'active', 'default_variant']):
        """
        Gets a products by its id.

        .. note::
            If not all products where found an exception is thrown,
            which contains a list of all found and all not found products.

        :param list pids: A list of product ids.
        :returns: A list of :py:class:`aboutyou.easy.Product` instance.
        :throws: :py:class:`aboutyou.easy.SearchException`

        .. rubric:: Example

        .. code-block:: python

            try:
                for p in easy.productsById([237188, 237116]):
                    print p.name
            except SearchException as e:
                print e.withError   # list of tuples (id, [errors]) for not found products
                print e.found       # list of found products
        """
        spid = []
        products = []
        withError = []

        # get products from cache or mark unknown products
        if self.cache is not None:
            for pid in pids:
                sid = str(pid)
                p = self.cache.get(sid)

                if p is None:
                    spid.append(sid)
                else:
                    products.append(p)
        else:
            spid = [str(p) for p in pids]

        if len(spid) > 0:
            response = self.aboutyou.products(ids=pids, fields=list(fields))

            for pid, p in response["ids"].items():
                if "error_message" in p:
                    withError.append((pid, p['error_message']))
                else:
                    products.append(Product(self, p))

            if self.cache is not None:
                for n in new:
                    self.cache.set(str(n.id), n, self.config.cache['timeout'])


        if len(withError) > 0:
            raise SearchException('not all products were found', products, withError)

        return products


    def productsByEAN(self, eans):
        """
        Gets products by its ean code.

        :param int ean: Product ean.
        :returns: A :py:class:`aboutyou.easy.Product` instance.
        """
        response = self.aboutyou.producteans(eans=eans)

        return [Product(self, p) for p in response]


    def search(self, sessionid, filter=None, result=None):
        """
        Creates a new :py:class:`aboutyou.easy.Search` instance.

        .. note:: See :py:func:`aboutyou.aboutyou.productsearch`.

        :param sessionid: The user session id.
        :returns: A :py:class:`aboutyou.easy.Search` instance.
        """
        return Search(self, sessionid, filter, result)


    def autocomplete(self, searchword, types=None, limit=None):
        """
        Autocompletes the searchword and looks in the products and/or
        categories for autocompletion possebilities.

        :param str searchword: The abbriviation.
        :param list types: against which types should be autocompleted.
                            The oprions are :py:class:`aboutyou.Constants.TYPES`
        :param int limit: the amount of items returned per selected type
        :returns: A tuple of two list. First one are the products and the second
                 are the categories.

        .. rubric:: Example

        .. code-block:: python

            >>> products, categories = easy.autocomplete("sho")
        """
        result = self.aboutyou.autocomplete(searchword,
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
                    raise AboutYouException("unknown category {}".format(scid))

        return products, categories

    def suggest(self, searchword, categories=None, limit=None):
        """
        Suggest additional words to the provided searchword.

        :param str searchword: A search string to suggest items for.
        :param list categories: A list of :py:class:`aboutyou.easy.Category`.
        :param int limit: The maximum amount of results.
        :returns: A list of strings.
        """
        if categories is not None:
            categoriescast = [c.id for c in categories]
        else:
            categoriescast = None

        result = self.aboutyou.suggest(searchword,
                                      categories=categoriescast,
                                      limit=limit)
        return result
