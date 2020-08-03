from typing import Dict, List
from itertools import chain as itt_chain
from datetime import date, datetime


DEFAULT_KEY_IDS: Dict[str, List[str]] = {
    'key' : ['key'], 'string' : ['string'],
    'data' : ['data'], 'dict' : ['dict'],
    'array' : ['array'], 'int' : ['integer'],
    'true' : ['true'], 'false' : ['false'],
    'float' : ['real'], 'date' : ['date']
}

DEFAULT_KEYS: List[str] =  ['key', 'string', 'data', 'dict', 'array', 'integer',
                            'true', 'false', 'real', 'date']

TYPE_TO_KEYNAME = {
    int: 'int', str: 'string',
    bytes: 'data', bytearray: 'data',
    float: 'float', date: 'date',
    datetime: 'date'
}


def updatekeys(newdefs: Dict[str, List[str]]) -> None:
    '''Update the namespace for 'plist' tag definitions.

    Parameters
    ----------
    newdefs : Dict[str, List[str]]
        Dictionary that contains new tag definitions. The dictionary may be
        incomplete, and therefore the old dictionary is being updated with the
        new, using `dict.update` method. The value linked to the directory keys
        is a list containing all tags associated with a 'plist' type. The first
        value in the list is going to be used when automatically creating new
        `PlistElement` objects.
    '''
    global DEFAULT_KEYS
    global DEFAULT_KEY_IDS

    # Solution for all python 3.x versions
    DEFAULT_KEY_IDS.update(newdefs)
    DEFAULT_KEYS[:] = list(itt_chain(*DEFAULT_KEY_IDS.values()))