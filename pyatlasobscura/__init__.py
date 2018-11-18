from typing import Generator

import requests
from bs4 import BeautifulSoup

from pyatlasobscura.models.destinations import Region


class Client(object):
    Endpoint = "https://www.atlasobscura.com/"

    def __init__(self, pandas_mode=False):
        self._cache = {}
        self._pandas_mode = pandas_mode

    def query(self, path, args={}):
        body = requests.get(self._build_url(path), params=args)
        return BeautifulSoup(
            markup=body.content.decode('utf-8', 'ignore'),
            features='html.parser'
        )

    def _build_url(self, path):
        return self.Endpoint + path

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

    def find_country(self, country_name):
        for region in self.regions():
            for country in region.countries:
                if country.name == country_name:
                    return country


_client = Client()


def destinations():
    return _client.regions()
