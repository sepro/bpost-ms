def find(key, dictionary):
    """
    Generator to extract items from complex nested data structures

    source: https://stackoverflow.com/questions/9807634/find-all-occurrences-of-a-key-in-nested-python-dictionaries-and-lists

    :param key: Key to look for
    :param dictionary: Object with nested dicts and lists
    :return: generator with all values matching the desired key
    """
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                if isinstance(d, dict) or isinstance(d, list):
                    for result in find(key, d):
                        yield result
