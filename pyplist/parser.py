from typing import Dict, Union, List, no_type_check
from re import compile as re_compile, match as re_match
from xml.parsers.expat import ParserCreate, error as expat_error

from . import APTypes
from .tree import PlistElement, dateobj
from .namespace import *


def _dicterror(element: PlistElement) -> bool:
    '''Check if a 'NSDictionary' is valid. `True` is returned when a error is
    found.'''

    if not element.tag in DEFAULT_KEY_IDS['dict']:
        raise ValueError('`element` is not a dict')
    if len(element._children) == 0:     return False
    keys: List[PlistElement] = element._children[::2]
    values: List[PlistElement] = element._children[1::2]
    if len(keys) != len(values):        return True
    # Check if all keys are valid Plist keys and check if values that those
    # keys point at, are not Plist keys. If not return False
    validks: bool = all([key.tag in DEFAULT_KEY_IDS['key'] for key in keys])
    validvs: bool = all([value.tag not in DEFAULT_KEY_IDS['key'] for value in values])
    return (not validks or not validvs)

def _dictattrstoxml(input: Dict[str, str]) -> str:
    '''Convert dictionary attributes to string 'xml' attributes'''

    if not input: return ''
    # Escape `"` and `'` with \
    return ''.join([' %s="%s"' % (k, v.replace('"', '\\"'))\
        for k,v in input.items()])


class PlistXML():
    '''Parser class that implements `fromstring` and `fromfile` methods by using
    the `expat` parser.

    Attributes
    ----------
    _parser : object
        Fully constructed expat parser object that has all member functions
        linked to it.
    _orderelementlist : List[PlistElement]
        A ordered list that contains every directory node. When a new
        `PlistElement` object has been parsed, it is appended to the end of this
        list and if the parsed `PlistElement` object is not a directory node, it
        is being removed from the list and added as a sub-node to the
        `PlistElement` before the removed element.
    '''

    def __init__(self) -> None:
        # Try to import 'expat' module from different directories

        # Build the expat parser object by linking the handling functions to it
        parser = ParserCreate(None, "}")
        parser.DefaultHandlerExpand = None
        parser.StartElementHandler = self._start
        parser.EndElementHandler = self._end
        parser.CharacterDataHandler = self._data

        # Thanks to 'xuanyuanzhiyuan' (https://stackoverflow.com/a/8571649)
        self._b64check = re_compile(
            r'^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$')
        self._parser = parser
        self._orderelementlist: List[PlistElement] = []

    def parse(self, source: str, validate_dicts: bool = True) -> PlistElement:
        '''Read the string and parse it using `expat`'''
        self._validate_dicts = validate_dicts
        try:                        self._parser.Parse(source, True)
        except expat_error as e:    raise SyntaxError("String cannot be parsed")

        # Return root
        return self._orderelementlist[0]

    def parsefile(self, filename: str, validate_dicts: bool = True) -> PlistElement:
        '''Read the target file and parse it using `expat`'''
        self._validate_dicts = validate_dicts
        buffer: str = open(filename, 'r').read()

        try:                        self._parser.Parse(buffer, True)
        except expat_error as e:    raise SyntaxError("'%s' cannot be parsed" % filename)

        # Return root
        return self._orderelementlist[0]

    def _start(self, tag: str, attr_list: Dict[str, str]) -> None:
        '''Parser handler method that creates new objects when a opening tag
        was parsed by `expat`'''
        # Ignore `plist` tag. It is intended to be a identificator
        if tag.lower() == "plist":  return
        self._orderelementlist.append(PlistElement(tag, \
            attribs=attr_list, parsedobj=True))
    def _end(self, tag: str) -> None:
        '''Parser handler method that closes and appends the object to its
        parent'''

        if tag in DEFAULT_KEY_IDS['dict'] and self._validate_dicts:
            if _dicterror(self._orderelementlist[-1]):
                raise SyntaxError("Parsed 'NSDictionary' is not valid")

        # If there is a parent element add the last element to it
        if len(self._orderelementlist) > 1:
            tmpobj: PlistElement = self._orderelementlist.pop()
            self._orderelementlist[-1]._children.append(tmpobj)

            if self._orderelementlist[-1].tag in DEFAULT_KEY_IDS['dict'] \
                and tmpobj.tag in DEFAULT_KEY_IDS['key']:
                # Link the key to the element after the key that is supposed to
                # be the hypotetical value. When the linked value is a key and
                # `_validate_dicts` is set to False, errors may occur. Set
                # `_validate_dicts` to False only if you know that the property
                # list is valid
                self._orderelementlist[-1]._dictitems[tmpobj.text] = self._orderelementlist[-1]._children.index(tmpobj) + 1 # type: ignore
    def _data(self, data: str) -> None:
        '''Parser handler method that appends inner xml text to `PlistElement`
        `text` attribute'''

        data = data.strip()
        # Ignore empty data
        if data == '':    return
        target: PlistElement = self._orderelementlist[-1]
        if target.tag in DEFAULT_KEY_IDS['date']:
            target.text = dateobj(data)
            return
        elif target.tag in DEFAULT_KEY_IDS['data']:
            if not re_match(self._b64check, data):
                raise ValueError('`%s` is not valid base64' % data)
            super(PlistElement, target).__setattr__('text', data)
            return
        target.text = data