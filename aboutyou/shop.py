#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]

ShopApi is the attempt to make Api a little bit more userfriendly
and hides much of the direct calls to the Api API.


Class Structures
----------------

.. digraph:: objects

    node[shape=none];

    shop[label=<<table cellspacing="0" border="0" cellborder="1">
        <tr><td colspan="2">ShopApi</td></tr>
        <tr><td>categories()</td><td></td></tr>
        <tr><td>category_by_id()</td><td></td></tr>
        <tr><td>category_by_name()</td><td></td></tr>
        <tr><td>facet_group_by_id()</td><td></td></tr>
        <tr><td>products_by_id()</td><td></td></tr>
        <tr><td>products_by_ean()</td><td></td></tr>
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
from .api import Api, ApiException
from .config import Config
from .constants import PRODUCT_FIELD, TYPE
import bz2
import json
import uuid


class Node(object):
    """A simple wrapper around a dict object."""

    def __init__(self, shop, obj):
        self.shop = shop
        self.obj = obj

        if "error_message" in obj or "error_code" in obj:
            raise ApiException("{} {}".format(obj["error_code"], obj["error_message"]))

    def __getattr__(self, name):
        return self.obj[name]

    def __getitem__(self, idx):
        return self.obj[idx]


class Category(Node):
    """
    The representation of a category in the category tree.
    """
    def __init__(self, shop, obj):
        super(Category, self).__init__(shop, obj)

        self.sub_categories = []

    def treeiter(self):
        """
        Walks the whole tree beginning from this node.

        :return: A tuple (level, :py:class:`aboutyou.shop.Category`).
        """
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
    def __init__(self, fid, name, facets):
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


class Image(Node):
    """
    Represents an image.
    """
    def __init__(self, shop, obj):
        super(Image, self).__init__(shop, obj)

    def url(self, width=None, height=None):
        """
        Returns the url to the image.
        """
        url = self.shop.api.config.image_url.format(self.hash)
        sizes = []

        if width:
            sizes.append('width={}'.format(width))

        if height:
            sizes.append('height={}'.format(height))

        if len(sizes) > 0:
            url += '?' + '&'.join(sizes)

        return url

    def __str__(self):
        return self.shop.api.config.image_url.format(self.hash)

    def __unicode__(self):
        return self.shop.api.config.image_url.format(self.hash)


class VariantAttributes(object):
    def __init__(self, shop, obj):
        self.obj = obj
        self.shop = shop

        prefixlen = len("attributes_")
        self.__data = {}

        for name, value in obj.items():
            grpid = int(name[prefixlen:])
            facets = shop.facet_group_by_id(grpid)

            collection = []
            for f in value:
                g = facets.facets.get(f, None)

                if g is None:
                    g = Node(shop, {'id': facets.id,
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


class Variant(Node):
    """
    A variant of a Product.
    """
    def __init__(self, shop, obj):
        super(Variant, self).__init__(shop, obj)

        self._hash = obj['id']
        self._images = [Image(shop, i) for i in obj["images"]]
        self._attributes = VariantAttributes(shop, obj["attributes"])

    @property
    def images(self):
        """
        An array of :py:class:`aboutyou.shop.Image`.
        """
        return self._images

    @property
    def attributes(self):
        """
        The attributes aka facets of this product variant.
        """
        return self._attributes

    def live(self):
        """
        The live data to this variant.
        """
        return self.shop.api.livevariant([self.id])

    def costumize(self):
        """
        Returns a costumizeable instance of this variant.

        :return: :py:class:`aboutyou.shop.CostumizedVariant`
        """
        return CostumizedVariant(self)

    def __hash__(self):
        return self._hash


class CostumizedVariant(Variant):
    def __init__(self, variant):
        # super(type(self), self).__init__(variant.shop, variant.obj)
        self.obj = variant.obj
        self.shop = variant.shop
        self._images = variant._images
        self._attributes = variant._attributes

        # if we use uuid directly.
        # we get a "OverflowError: Python int too large to convert to C long"
        # when used with dictonarys.
        self._hash = hash(uuid.uuid4())

        self.additional_data = {'description': 'costumized'}

    def __hash__(self):
        return self._hash


class Product(Node):
    """
    A product with its variants.

    .. note::

        The Product class is an extensive user of the auto_fetch feature.
        If enabled in the configuration, when accessing a field which data
        is not present, for example the variants, then the variants will be
        automaticly request.
    """
    def __init__(self, shop, obj):
        super(Product, self).__init__(shop, obj)

        self.__variants = None
        self.__categories = None
        self.__short_description = None
        self.__long_description = None
        self.__default_image = None
        self.__default_variant = None
        self.__styles = None

    def url(self):
        """
        Returns the url to the product in the shop.
        """
        slug = self.name.strip().replace(" ", "-") + "-" + str(self.id)
        return self.shop.api.config.product_url.format(slug)

    def __update_cache(self):
        if self.shop.cache:
            self.shop.cache.set(str(self.obj['id']), self.obj,
                                self.shop.config.cache['timeout'])

    @property
    def categories(self):
        """
        :returns: A list of :py:class:`aboutyou.shop.Category`.
        """
        if self.__categories is None:
            catname = "categories.{}".format(self.shop.credentials.app_id)

            if catname not in self.obj and self.shop.config.auto_fetch:
                self.shop.api.log.debug('update categories from product %s', self.obj['id'])
                data = self.shop.api.products(ids=[self.id],
                                                   fields=[PRODUCT_FIELD.CATEGORIES])
                self.obj.update(data["ids"][str(self.id)])

                self.__update_cache()

            self.__categories = [[self.shop.category_by_id(cid) for cid in path] for path in self.obj[catname]]

        return self.__categories

    @property
    def variants(self):
        """
        :returns: A list of :py:class:`aboutyou.shop.Variant`.
        """
        if self.__variants is None:

            if "variants" not in self.obj and self.shop.config.auto_fetch:
                self.shop.api.log.debug('update variants from product %s', self.obj['id'])
                data = self.shop.api.products(ids=[self.id],
                                                   fields=[PRODUCT_FIELD.VARIANTS])
                self.obj.update(data["ids"][str(self.id)])

                self.__update_cache()


            self.__variants = [Variant(self.shop, v) for v in self.obj["variants"]]

        return self.__variants

    @property
    def default_image(self):
        """
        The default image of this product.
        :returns: :py:class:`aboutyou.shop.Image`
        """
        if self.__default_image is None:
            if "default_image" not in self.obj and self.shop.config.auto_fetch:
                self.shop.api.log.debug('update default_image from product %s', self.obj['id'])
                data = self.shop.api.products(ids=[self.obj['id']],
                                                   fields=[PRODUCT_FIELD.DEFAULT_IMAGE])
                self.obj.update(data["ids"][str(self.id)])

                self.__update_cache()

            self.__default_image = Image(self.shop, self.obj["default_image"])

        return self.__default_image

    @property
    def default_variant(self):
        """
        The default variant of this product.

        :returns: :py:class:`aboutyou.shop.Variant`
        """
        if self.__default_variant is None:
            if "default_variant" not in self.obj and self.shop.config.auto_fetch:
                self.shop.api.log.debug('update default_variant from product %s', self.obj['id'])
                data = self.shop.api.products(ids=[self.obj['id']],
                                                   fields=[PRODUCT_FIELD.DEFAULT_VARIANT])
                self.obj.update(data["ids"][str(self.obj['id'])])

                self.__update_cache()

            self.__default_variant = Variant(self.shop, self.obj["default_variant"])

        return self.__default_variant

    @property
    def styles(self):
        """
        The styles of this product.
        """
        if self.__styles is None:
            if "styles" not in self.obj and self.shop.config.auto_fetch:
                data = self.shop.api.log.debug('update styles from product %s', self.obj['id'])

                self.obj.update(data["ids"][str(self.obj['id'])])

                self.__update_cache()

            styles = []

            for pobj in self.obj['styles']:
                if self.shop.cache:
                    tmp = self.shop.cache.get(str(pobj['id']))

                    if tmp is None:
                        product = Product(self.shop, pobj)
                        self.shop.cache.set(str(product.id), pobj, self.shop.config.cache['timeout'])
                    else:
                        product = Product(self.shop, tmp)
                else:
                    product = Product(self.shop, pobj)

                styles.append(product)

            self.__styles = styles

        return self.__styles

    def __getattr__(self, name):
        if not name.startswith('__') and name not in self.obj and self.shop.config.auto_fetch:
            self.shop.api.log.debug('update %s from product %s', name, self.obj['id'])
            data = self.shop.api.products(ids=[self.obj['id']],
                                               fields=[PRODUCT_FIELD.DESCRIPTION_SHORT,
                                                       PRODUCT_FIELD.DESCRIPTION_LONG,
                                                       PRODUCT_FIELD.SALE])
            self.obj.update(data["ids"][str(self.obj['id'])])

            self.__update_cache()

        return self.obj[name]

    def __hash__(self):
        return self.obj['id']


class SearchException(Exception):
    """
    An exception thrown by products_by_id.

    :param msg: An error message
    :param found: The products with error.
    :param withError: The products with error.
    """
    def __init__(self, msg, found, withError):
        super(SearchException, self).__init__(msg)
        self.found = found
        self.withError = withError


class ResultProducts(object):
    def __init__(self, search):
        self.search = search
        self.buffer = []

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

            gather_start = len(self.buffer)

            if gather_start < stop:
                pos = gather_start
                count = stop - gather_start

                for i in xrange(count / 200):
                    self.search.gather(pos, 200)
                    pos += 200

                if count % 200 != 0:
                    self.search.gather(pos, 200)

            return [self.buffer[i] for i in xrange(start, stop, step)]

        if self.buffer[idx] is None:
            self.search.gather(idx, 1)

        return self.buffer[idx]

    def __len__(self):
        return self.search.count

    def __iter__(self):
        step = 200
        i = 0
        # 'for' will not work, because 'count' can change each gather call.
        # for i in xrange(0, self.search.count):
        while i < self.search.count:
            if len(self.buffer) <= i:
                self.search.gather(i, step)

            yield self.buffer[i]
            i += 1


class Search(object):
    """
    Representing an initiated search.
    """
    def __init__(self, shop, sessionid, filter=None, result=None):
        self.shop = shop
        self.sessionid = sessionid
        self.filter = filter
        self.categories = {}

        if result is None:
            self.result = {"limit": 0, "offset": 0}
        else:
            self.result = result
            self.result["limit"] = 0
            self.result["offset"] = 0

        self.obj = self.shop.api.productsearch(self.sessionid,
                                                    filter=self.filter,
                                                    result=self.result)

        self.count = self.obj["product_count"]

        self.products = ResultProducts(self)

        if "categories" in self.obj["facets"]:
            for el in self.obj["factes"]["categories"]:
                cat = self.shop.category_by_id(el["term"])
                self.categories[cat] = el["count"]


    def gather(self, offset, limit):
        self.result['offset'] = offset
        self.result['limit'] = limit

        self.shop.api.log.debug('gather %s %s %s',
                                     self.sessionid, self.filter, self.result)

        response = self.shop.api.productsearch(self.sessionid,
                                                    filter=self.filter,
                                                    result=self.result)

        # the result count can change ANY request !!!
        self.count = response['product_count']

        self.shop.api.log.debug('result count %s : %s', len(response['products']), response['product_count'])

        for p in response["products"]:
            product = None

            if self.shop.cache is not None:
                product = self.shop.cache.get(str(p["id"]))

            if product is None:
                product = Product(self.shop, p)

                if self.shop.cache is not None:
                    self.shop.cache[str(product.id)] = product

            self.products.buffer.append(product)


class BasketException(Exception):
    def __init__(self, msg, fine, withError):
        super(BasketException, self).__init__(msg)

        self.fine = fine
        self.withError = withError


class Basket(object):
    """
    :param shop: The ShopApi instance.
    :param sessionid: The session id the basket is associated with.
    """
    def __init__(self, shop, sessionid):
        self.shop = shop
        self.sessionid = sessionid
        self.obj = None

        self.variants = {}
        self.basket_ids_by_variant = {}

    def __getattr__(self, name):
        return self.obj[name]

    def _check_obj(self):
        withError = []
        fine = []

        for line in self.obj['order_lines']:
            if 'error_message' in line:
                withError.append(line)
            else:
                fine.append(line)

        if len(withError) > 0:
            msg = '\n'.join((i['error_message'] for i in withError))
            self.shop.api.log.error(msg)
            self.shop.api.log.error(json.dumps(self.obj, indent=4))
            raise BasketException(msg, fine, withError)

    def set(self, variant, count):
        """
        Sets the *count* of the *variant* in the basket.

        :param variant: :py:class:`aboutyou.shop.Variant` or :py:class:`aboutyou.shop.CostumVariant`
        :param int count: The amount of the items. If set to 0 the item is removed.
        """
        def push_ids(ids):
            vid = variant.id
            if isinstance(variant, CostumizedVariant):
                additional = variant.additional_data
                basketset = [(i, vid, additional) for i in ids]
            else:
                basketset = [(i, vid) for i in ids]

            self.obj = self.shop.api.basket_set(self.sessionid, basketset)


        if count < 1 and variant in self.basket_ids_by_variant:
            self.obj = self.shop.api.basket_remove(self.sessionid, self.basket_ids_by_variant[variant])

            del self.basket_ids_by_variant[variant]
            del self.variants[variant]

        else:
            if variant in self.variants:
                delta = count - self.variants[variant]

                if delta > 0:
                    ids = [uuid.uuid4().hex for unused in xrange(delta)]
                    self.basket_ids_by_variant[variant] += ids

                    push_ids(ids)

                elif delta < 0:
                    to_remove = self.basket_ids_by_variant[variant][:-delta]
                    self.basket_ids_by_variant[variant] = self.basket_ids_by_variant[variant][-delta:]

                    self.obj = self.shop.api.basket_remove(self.sessionid, to_remove)

            else:
                self.variants[variant] = count

                ids = [uuid.uuid4().hex for unused in xrange(count)]
                self.basket_ids_by_variant[variant] = ids

                push_ids(ids)

            self._check_obj()


    def buy(self, success_url, cancel_url=None, error_url=None):
        """
        Begins to order this basket.

        :param str success_url: this is a callback url if the order was successfully created.
        :param str cancel_url: this is a callback url if the order was canceled.
        :param str error_url: this is a callback url if the order throwed exceptions.
        :returns: The url to the shop.
        """
        self.shop.api.log.debug('buy basket %s', self.sessionid)
        return self.shop.api.order(self.sessionid, success_url, cancel_url, error_url)

    def dispose(self):
        """
        Removes all items from the basket and disassociates this basket with the session id.
        """
        self.shop.api.log.debug('dispose basket %s', self.sessionid)

        self.shop.api.basket_dispose(self.sessionid)

        del self.shop._baskets[self.sessionid]


class ShopApi(object):
    """
    An abstraction layer around the thin Api api.

    .. note::

        If caching is not set to *null* in the config file, ShopApi will
        cache Factes and the Category-Tree.

    :param config: A :py:class:`aboutyou.config.Config` instance.
    :param credentials: A :py:class:`aboutyou.config.Credentials` instance.
    """
    def __init__(self, credentials, config=Config()):
        self.credentials = credentials
        self.config = config
        self.api = Api(self.credentials, self.config)

        self.__categorytree = None
        self.__category_ids = {}
        self.__category_names = {}

        self.__facet_map = None
        self.__facet_groups = []

        self.__simple_colors = None

        self._baskets = {}

        self.cache = None

        if self.config.cache is not None and len(self.config.cache) > 0:
            try:
                import pylibmc

                self.cache = pylibmc.Client(self.config.cache['hosts'],
                                            binary=True,
                                            behaviors={"tcp_nodelay": True, "ketama": True})
                self.cache.get('TEST_TOKEN')
                self.api.log.info('use memcached via pylibmc')
            except:
                self.cache = None
                self.api.log.exception('')

    def __build_categories(self):
        tree = None

        if self.cache is not None:
            tree = self.cache.get('categorytree')

            if tree:
                tree = json.loads(bz2.decompress(tree))
                self.api.log.info('cached category tree')

        if tree is None:
            self.api.log.info('get category tree from Api')
            tree = self.api.categorytree()

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
            if facets:
                facets = json.loads(bz2.decompress(facets))
                response = json.loads(bz2.decompress(response))
                self.api.log.info('cached facets')

        if facets is None:
            # facets = self.api.facettypes()
            response = self.api.facets([])["facet"]

            if self.cache is not None:
                self.cache.set('facettypes', bz2.compress(json.dumps(facets)),
                               self.config.cache['timeout'])
                self.cache.set('facets', bz2.compress(json.dumps(response)),
                               self.config.cache['timeout'])

        self.__facet_map = {}
        for facet in response:
            fobj = Node(self, facet)
            group = self.__facet_map.get(fobj.group_name)
            if group is None:
                group = FacetGroup(fobj.id, fobj.group_name, {})
                self.__facet_map[group.name] = group
                self.__facet_map[group.id] = group
                self.__facet_groups.append(group)

            group.facets[fobj.facet_id] = fobj


    def basket(self, sessionid):
        """
        Returns a basket for the session id.

        :param sessionid: The session id the basket is associated with.
        :returns: :py:class:`aboutyou.shop.Basket`
        """
        if sessionid in self._baskets:
            return self._baskets[sessionid]
        else:
            basket = Basket(self, sessionid)

            self._baskets[sessionid] = basket

            return basket


    def categories(self):
        """
        Returns the category tree.

        :returns: A list of :py:class:`aboutyou.shop.Category`.
        """
        if self.__categorytree is None:
            self.__build_categories()

        return self.__categorytree


    def category_by_id(self, cid):
        """
        Returns the category with the given id.

        :param cid: The id of the category to get.
        :returns: A :py:class:`aboutyou.shop.Category` instance.
        """
        if self.__categorytree is None:
            self.__build_categories()

        return self.__category_ids[cid]

    def category_by_name(self, name):
        """
        Returns the category with the given name.

        .. note:: If there are more than one category with the same name.
                    The last inserted category will be returned.

        :param str name: The name of the category.
        :returns: A :py:class:`aboutyou.shop.Category` instance.
        """
        if self.__categorytree is None:
            self.__build_categories()

        return self.__category_names[name]

    def simple_colors(self):
        """
        Returns an array of facet colors which are a simple selection out
        of the hugh possebilities.
        """
        if self.__facet_map is None:
            self.__build_facets()

        if self.__simple_colors is None:
            self.api.log.info('build simple colors')

            colors = self.facet_group_by_id('color')
            self.__simple_colors = []
            for fid in [570, 168, 67, 247, 48, 14, 18, 204, 30, 1, 579, 15, 12,
                        11, 55, 580, 9, 333, 646]:
                self.__simple_colors.append(colors[fid])

        return self.__simple_colors


    def facet_groups(self):
        """
        :retuns: A set of all known facet groups.
        """
        if self.__facet_map is None:
            self.__build_facets()

        return self.__facet_groups


    def facet_group_by_id(self, facet_group):
        """
        Returns all facets of a group.

        :param facet_group: The id or name of the facet group.
        :returns: A :py:class:`aboutyou.shop.FacetGroup` instance.
        """
        if self.__facet_map is None:
            self.__build_facets()

        return self.__facet_map[facet_group]


    def products_by_id(self, pids, fields=['sale', 'active', 'default_variant']):
        """
        Gets a products by its id.

        .. note::
            If not all products where found an exception is thrown,
            which contains a list of all found and all not found products.

        :param list pids: A list of product ids.
        :returns: A list of :py:class:`aboutyou.shop.Product` instance.
        :throws: :py:class:`aboutyou.shop.SearchException`

        .. rubric:: Example

        .. code-block:: python

            try:
                for p in shop.products_by_id([237188, 237116]):
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
                    products.append(Product(self, p))
        else:
            spid = [str(p) for p in pids]

        if len(spid) > 0:
            response = self.api.products(ids=pids, fields=list(fields))
            new = []

            for pid, p in response["ids"].items():
                if "error_message" in p:
                    withError.append((pid, p['error_message']))
                else:
                    product = Product(self, p)
                    new.append(product)
                    products.append(product)

            if self.cache is not None:
                for n in new:
                    self.cache.set(str(n.id), n.obj)#, self.config.cache['timeout'])


        if len(withError) > 0:
            raise SearchException('not all products were found', products, withError)

        return products


    def products_by_ean(self, eans):
        """
        Gets products by its ean code.

        :param int ean: Product ean.
        :returns: A :py:class:`aboutyou.shop.Product` instance.
        """
        response = self.api.producteans(eans=eans)

        return [Product(self, p) for p in response]


    def search(self, sessionid, filter=None, result=None):
        """
        Creates a new :py:class:`aboutyou.shop.Search` instance.

        .. note:: See :py:func:`Api.Api.productsearch`.

        :param sessionid: The user session id.
        :returns: A :py:class:`aboutyou.shop.Search` instance.
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

            >>> products, categories = shop.autocomplete("sho")
        """
        result = self.api.autocomplete(searchword,
                                            types=types,
                                            limit=limit)

        products = []
        if types is None or TYPE.PRODUCTS in types:
            for p in result["products"]:
                pobj = Product(self, p)
                products.append(pobj)

        categories = []
        if types is None or TYPE.CATEGORIES in types:
            if self.__categorytree is None:
                self.__build_categories()

            for c in result["categories"]:
                scid = c["id"]

                if scid in self.__category_ids:
                    categories.append(self.__category_ids)
                else:
                    raise ApiException("unknown category {}".format(scid))

        return products, categories

    def suggest(self, searchword, categories=None, limit=None):
        """
        Suggest additional words to the provided searchword.

        :param str searchword: A search string to suggest items for.
        :param list categories: A list of :py:class:`aboutyou.shop.Category`.
        :param int limit: The maximum amount of results.
        :returns: A list of strings.
        """
        if categories is not None:
            categoriescast = [c.id for c in categories]
        else:
            categoriescast = None

        result = self.api.suggest(searchword,
                                       categories=categoriescast,
                                       limit=limit)
        return result
