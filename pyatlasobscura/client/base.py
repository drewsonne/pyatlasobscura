import hashlib
from abc import ABC

import requests
from bs4 import BeautifulSoup

from pyatlasobscura import cache


class BaseClient(ABC):
    _endpoint = "https://www.atlasobscura.com/"

    def __init__(self):
        self._cache = {}

    def query(self, path, args=None) -> BeautifulSoup:
        if args is None:
            args = {}

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
