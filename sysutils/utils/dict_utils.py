"""
copyright tretyak@gmail.com
"""

import collections


def multi_dict_as_dict(md):
    """
    See http://aiohttp.readthedocs.io/en/v0.21.5/multidict.html#aiohttp.MultiDictProxy
    """
    return {k: md[k] for k in iter(md)}


def get_or_create(data: dict, key):
    value = data.get(key)
    if not value:
        data[key] = {}
    return data[key]

def safeget(dct, *keys, **kwargs):
    """
    function get for included dict
    :param dct:
    :param keys:
    :return: None if no key
    """
    default = kwargs.get('default', None)
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return default
    return dct or default


def dict_merge(merge_to, merge_from):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurse down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_from`` is merged into
    ``merge_to``.
    :param merge_to: dict onto which the merge is executed
    :param merge_from: merge_to merged into merge_to
    :return: merge_to
    """
    for k, v in merge_from.items():
        if (k in merge_to and isinstance(merge_to[k], dict)
                and isinstance(merge_from[k], collections.Mapping)):
            dict_merge(merge_to[k], merge_from[k])
        else:
            merge_to[k] = merge_from[k]
    return merge_to


def walk(node, leaf_perform):
    """ Walk through a dictionary(list) and perform action to each 'leaf' value
    :param node: <dict|list>
    :param leaf_perform: <function>
    :return: updated node
    """
    if isinstance(node, list):
        for item in node:
            walk(item, leaf_perform)
    elif isinstance(node, dict):
        for key, item in list(node.items()):
            node[key] = walk(item, leaf_perform)
    else:
        node = leaf_perform(node)
    return node


def walk_through(node: [dict, list], leaf_perform: callable, path: str = None):
    """ Walk through a dictionary(list) and perform action to each 'leaf' value
    :param node: <dict|list>
    :param leaf_perform: <function>
    :param path: collect path from ROOT
    :return: updated node
    """
    path = path or ''
    separator = '' if not path else '.'

    if isinstance(node, list):
        for (i, item) in enumerate(node):
            walk_through(item, leaf_perform, path + "[{}]".format(i))
    elif isinstance(node, dict):
        for key, item in list(node.items()):
            node[key] = walk_through(item, leaf_perform, path + "{}{}".format(separator, key))
    else:
        node = leaf_perform(node, path)
    return node


if __name__ == "__main__":
    test = {"aaaa": {
        "bbb": {
            "ccc": 100,
            "bbb": 200,
        },
        "dddd": [
            {"AAAA": 888},
            {"BBBB": 999},
        ]
    }}

    def tester(value, path):
        print("VALUE:{:>10} PATH: {}".format(value, path))

    walk_through(test, tester)