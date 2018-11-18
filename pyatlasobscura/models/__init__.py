import json


class Model(object):
    id_keys = []

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

        # If that fails, return default behavior so we don't break Python
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getitem__(self, item):
        if item in self._data:
            return self._data[item]
        if item in self.lazy_load_facets:
            getattr(self, '_load_' + item)()
            return self[item]

    def load(self):
        self._lazy_load_all()
        return self

    def __repr__(self):
        return "<{module_name}.{class_name}({keys}) object at {hash}>".format(
            module_name=self.__module__,
            class_name=self.__class__.__name__,
            keys=','.join(map(
                lambda k: k + '=' + json.dumps(self[k]),
                self.id_keys
            )),
            hash=hex(id(self))
        )
