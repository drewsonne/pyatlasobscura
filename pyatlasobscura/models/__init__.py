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
