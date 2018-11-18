import json
import re


class JsonSerialisable(dict):
    def __init__(self, client):
        super().__init__()
        self._client = client
        self._data = {}

    def __getattr__(self, key):
        # First, try to return from _response
        try:
            return self[key]
        except KeyError:
            pass

        if key in self.lazy_load_facets:
            getattr(self, '_load_' + key)()
            return self[key]

        # If that fails, return default behavior so we don't break Python
        try:
            return self.__dict__[key]
        except KeyError:
            raise AttributeError(key)

    def __repr__(self):
        return json. \
            dumps(self, indent=4, ensure_ascii=False)

    def load(self):
        self._lazy_load_all()
        return self


class Region(JsonSerialisable):
    def __init__(self, client, dom):
        super().__init__(client)
        self['name'] = dom.find('h2').get_text(strip=True)
        self['countries'] = [Country(client, self, d) for d in dom.findAll('a', {'class': 'detail-md'})]


class Country(JsonSerialisable):

    def __init__(self, client, region, a):
        super().__init__(client)
        self['name'] = a.get_text(strip=True)
        self['region'] = region['name']
        self._href = a['href']
        self._sort_by_recent = False

    def places(self, sort_by_recent=False, page_num='1'):

        self._sort_by_recent = sort_by_recent

        for page_num in self._get_pages(page_num):
            if page_num == 'Next':
                break
            for place in self._iterate_places(page_num):
                yield place

    def _iterate_places(self, page):
        for place in self._get_places(page):
            latlng = place. \
                find('div', {'class': 'lat-lng'}). \
                get_text(strip=True).split(', ')

            yield Place(
                client=self._client,
                country=self,
                title=place.find('h3').find('span').get_text(strip=True),
                description=place.find('div', {'class': 'content-card-subtitle'}).get_text(strip=True),
                href=place['href'],
                location={
                    'name': place.find('div', {'class': 'place-card-location'}).get_text(strip=True),
                    'coordinates': [float(latlng[0]), float(latlng[1])],
                    'country': self['name'],
                    'region': self['region']
                }
            )

    def _get_places(self, page):
        return self._get_place_list(page). \
            find('section', {'class': 'geo-places'}). \
            findAll('a', {'class': 'content-card'})

    def _get_pages(self, page):
        pages = self._get_place_list(page). \
            find('nav', {'class': 'pagination'})
        if pages is None:
            return '1'
        return [p.get_text(strip=True) for p in pages.findAll('span')]

    def _get_place_list(self, page):
        url = self._href + '/places'
        args = {}
        if int(page) > 1:
            args['page'] = page

        if self._sort_by_recent:
            args['sort'] = 'recent'

        return self._client.query(url, args)


class Place(JsonSerialisable):
    lazy_load_facets = ['datePublished', 'dateModified', 'categories']

    def __init__(self, client, title, description, location, href, country=None, category=None):
        super().__init__(client)
        self['title'] = title
        self['description'] = description
        self['location'] = location

        self._href = href
        if country is not None:
            self.country = country

        if category is not None:
            self.category = category

        self._load_tags = self._load_place
        self._load_datePublished = self._load_tags
        self._load_dateModified = self._load_tags
        self._load_categories = self._load_tags
        self._lazy_load_all = self._load_tags

    def _load_place(self):
        place_body = self._client.query(self._href)
        ld_raw_json = place_body.find('script', {'type': "application/ld+json"}).get_text()
        ld = json.loads(ld_raw_json)
        self['datePublished'] = ld['datePublished']
        self['dateModified'] = ld['dateModified']
        self['categories'] = [Category(self._client, t) for t in ld['keywords']]

        json_script = place_body. \
            find('script', text=re.compile(r'AtlasObscura\.current_place')). \
            get_text(strip=True).split(' = ', 1)[1].split(';')[0]
        place_metadata = json.loads(json_script)
        self['id'] = place_metadata['id']
        country = self._client.find_country(place_metadata['country'])
        self['location']['country'] = country['name']
        self['location']['region'] = country['region']
        self['nearby_places'] = [
            Place(
                self._client,
                title=place['title'],
                description=place['subtitle'],
                href=place['url'].replace('https://www.atlasobscura.com', ''),
                country=self._client.find_country(place['country']),
                location={
                    'name': place['location'],
                    'country': place['country'],
                    'coordinates': list(place['coordinates'].values()),
                    'region': self._client.find_country(place['country'])['region']
                }
            )
            for place in
            place_metadata['nearby_places']
        ]


class Category(JsonSerialisable):

    def __init__(self, client, name):
        super().__init__(client)
        self['name'] = name
        self._client = client
        self._dom = {}

    def places(self, page_num='1'):

        for page_num in self._get_pages(page_num):
            if page_num == 'Next':
                break
            for place in self._iterate_places(page_num):
                yield place

    def _iterate_places(self, page):
        for place in self._get_places(page):
            latlng = place. \
                find('div', {'class': 'lat-lng'}). \
                get_text(strip=True).split(', ')

            yield Place(
                self._client,
                category=self,
                title=place.find('h3').find('span').get_text(strip=True),
                description=place.find('div', {'class': 'subtitle-sm'}).get_text(strip=True),
                href=place.find('a', {'class': 'content-card'})['href'],
                location={
                    'name': place.find('div', {'class': 'place-card-location'}).get_text(strip=True),
                    'coordinates': [float(latlng[0]), float(latlng[1])]
                }
            )

    def _get_places(self, page):
        grid = self._get_place_list(page). \
            find('div', {'data-component-type': 'categories-places'})
        places = grid.findAll('div', {'class': 'index-card-wrap'})
        return places

    def _get_pages(self, page):
        pages = self._get_place_list(page). \
            find('nav', {'class': 'pagination'})
        if pages is None:
            return '1'
        spans = pages.findAll('span')
        return [p.get_text(strip=True) for p in spans]

    def _get_place_list(self, page):
        if page not in self._dom:
            url = '/categories/' + self['name']
            args = {}
            if int(page) > 1:
                args['page'] = page

            self._dom[page] = self._client.query(url, args)
        return self._dom[page]
