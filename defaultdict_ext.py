from collections import defaultdict

"""
An "extended" defaultdict that accepts a default_factory with one argument,
that argument being the key that the default item is being created for.
Allows for extra flexibility in the generation of the default items.

Example: defaultdict_ext(lambda k: k)
"""
class defaultdict_ext(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        return self.default_factory(key)
