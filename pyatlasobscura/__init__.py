import hashlib
from enum import auto, Enum
from typing import Generator

import requests
from bs4 import BeautifulSoup

from pyatlasobscura.cache import cache
from pyatlasobscura.models.destinations import Region
from pyatlasobscura.models.query import Category, Point


class URL(str): pass




def destinations() -> Generator[Region, None, None]:
    return Client.default().regions()


class SearchType(Enum):
    CATEGORY = auto()
    LOCATION = auto()


def search(search_type: SearchType, value: str, attrs=None):
    attrs = {} if attrs is None else attrs
    client = Client.default()

    return {
        SearchType.CATEGORY: client.search_category,
        SearchType.LOCATION: client.search_location
    }[search_type](value, **attrs)
