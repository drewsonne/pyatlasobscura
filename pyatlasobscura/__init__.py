import hashlib
from typing import Generator

import requests
from bs4 import BeautifulSoup

from pyatlasobscura.cache import cache
from pyatlasobscura.models.destinations import Region
from pyatlasobscura.models.query import Category, Point


class URL(str): pass


class Client(object):
    _DEFAULT = None

    @classmethod
    def default(cls):
        if cls._DEFAULT is None:
            cls._DEFAULT = cls()
        return cls._DEFAULT

    _endpoint = "https://www.atlasobscura.com/"

    def __init__(self):
        self._cache = {}

    def query(self, path, args={}) -> BeautifulSoup:

        def query_callback():
            body = requests.get(self._build_url(path), params=args)
            return BeautifulSoup(
                markup=body.content.decode('utf-8', 'ignore'),
                features='html.parser'
            )

        try:
            key = path + str(args)
            key_encoded = key.encode()
            key_hash = hashlib.md5(key_encoded).hexdigest()

            query_callback = cache(key_hash)(
                query_callback
            )
        except Exception as e:
            pass

        return query_callback()

    def _build_url(self, path: str):
        return self._endpoint + path

    def search_category(self, category):
        if 'categories' not in self._cache:
            self._cache['categories'] = {}
        if category in self._cache['categories']:
            return self._cache['categories']

        cache = []
        for location in Category(self, category):
            cache.append(location)
            yield location

        # Don't store until we have the full set
        self._cache['categories'][category] = cache

    def search_location(self, location, nearby):
        return Point(self, location, nearby)

    def regions(self) -> Generator[Region, None, None]:
        if 'regions' not in self._cache:
            body = self.query('destinations')
            regions = body. \
                findAll('li', {'class': 'global-region-item'})
            self._cache['regions'] = regions
        else:
            regions = self._cache['regions']
        for region in regions:
            yield Region(self, region)

    def find_country(self, country_name: str):
        for region in self.regions():
            for country in region.countries:
                if country.name == country_name:
                    return country


def destinations() -> Generator[Region, None, None]:
    return Client.default().regions()


def search(category=None, location=None, nearby=True):
    if category is not None:
        return Client.default().search_category(category)
    if location is not None:
        return Client.default().search_location(location, nearby)
