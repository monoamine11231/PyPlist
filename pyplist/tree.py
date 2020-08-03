from __future__ import annotations
from typing import List, Dict, Union, Generator, ItemsView, Optional, \
Tuple, Any, no_type_check
from base64 import b64encode, b64decode
from datetime import date, datetime

from . import APTypes
from .namespace import *


def dateobj(source: str) -> Union[date, datetime]:
    '''Parse `date` or `datetime` string to it's corresponding class'''
    try:
        return date.fromisoformat(source)
    except ValueError:
        return datetime.fromisoformat(source)

def isbool(element: PlistElement) -> bool:
    '''Returns `True` if the `element.tag` is defined inside 'NSBool' tag
    definitions'''

    return element.tag in (DEFAULT_KEY_IDS['true'] + DEFAULT_KEY_IDS['false'])

def isdirectory(element: PlistElement) -> bool:
    '''Returns `True` if the `element.tag` is defined inside 'NSArray' and
    'NSDictionary' tag definitions'''

    return element.tag in (DEFAULT_KEY_IDS['array'] + DEFAULT_KEY_IDS['dict'])


class PlistElement(object):
    '''
    `PlistElement` is a node class that supports all default 'plist' types, such
    as 'NSDictionary' and 'NSKey'. `PlistElement` is a duck typed extension of
    `xml.etree.ElementTree.Element`.

    Parameters
    ----------
    PLIST_TAG : str
        PLIST_TAG is used to initialize a `PlistElement` with the passed tag.
        PLIST_TAG is being checked if it is defined in the current key
        namespace (`DEFAULT_KEYS` global).
    text : Union[int, float, str, bytes, bytearray, date, datetime] = ""
        `text` holds the text of an 'xml/plist' element. `PlistElement`
        prohibits the use of the parameter in directory nodes, such as
        'NSDictionary' and 'NSArray'. `text` is being converted to an 'base64'
        string if the type is `bytes` or `bytearray`. If `text` is `date` or
        `datetime`, the `isoformat` method is being used to convert it to string
    attribs: Dict[str, str] = {}
        `attribs` are the parameters defined inside an 'xml/plist' tag and where
        the keys and values are being separated by a '='.
    parsedobj : bool = False
        `parsedobj` is an boolean identifier that is used to indicate that the
        `text` attribute is going to be set later by hand. It is intended to
        be used only while parsing strings or files, where the inner tag text is
        not known yet.

    Attributes
    ----------
    _dictitems : Dict[str, int]
        `_dictitems` is used only when a `PlistElement` is a type of
        'NSDictionary'. It points a string key to the index of the corresponding
        `PlistElement` in the `_children` list attribute.
    _children : List[PlistElement]
        `_children` is a list that holds all subnodes of a directory node.
        `_children` attribute is allowed only to be used if the `PlistElement`
        is a type of 'NSDictionary' or 'NSArray'.
    attrib : Dict[str, str]
        `attrib` holds the parameters that are being defined inside an
        'xml/plist' tag and where the keys and values are being separated by a
        '='.
    tag : str
        `tag` is the tag that the current `PlistElement` holds.
    text : str
        `text` is the text that is being placed between the opening and
        ending tag. It cannot be used if the `PlistElement` is not a directory
        node, such as 'NSDictionary' or 'NSArray'.
    tail : str
        Not used in this package, but reserved for a valid duck typed extension
        of `xml.etree.ElementTree.Element`
    '''

    _dictitems: Dict[str, int] = {}
    _children: List[PlistElement] = []
    attrib : Dict[str, str] = {}

    tag: str = ''
    tail: str = ''
    # `text` is only `str`. `date` and `datetime` are being wrapped inside to
    # prevent `mypy` warnings when trying to set `.text` attribute with a
    # `date` or `datetime` inside a 'NSDate' object. `__setattr__` is being
    # overloaded and `date` and `datetime` objects are being converted to string
    # with `isoformat` method
    text: Union[str, date, datetime] = ''

    def __init__(self, PLIST_TAG: str, text: APTypes = "",
        attribs : Dict[str, str] = {}, parsedobj: bool = False) -> None:
        if not PLIST_TAG in DEFAULT_KEYS:
            raise ValueError("`%s` not in current 'namespace'" % PLIST_TAG)
        if not isinstance(attribs, dict):
            raise ValueError("`attribs` parameter must be `dict`, not `%s`" %
            attribs.__class__.__name__)
        self._dictitems = {}
        self._children = []
        self.attrib = attribs
        super().__setattr__('tag', PLIST_TAG)

        # Ignore text errors if the object is created from parsing a string/file
        if parsedobj:   return

        self.text = text                                        # type: ignore

    def __setattr__(self, attr: str, value: APTypes) -> None:
        '''Forbids the change of the `tag` attribute and the set of `text`
        attribute in 'NSDictionary' and 'NSArray'. Value is being converted to
        a 'base64' string if the value is type of `bytes` or `bytearray`.

        Parameters
        ----------
        attr : str
            Attribute's name that is going to be set or changed in this class
        value : Union[int, float, str, bytes, bytearray, date, datetime]
            Value to be setted to the attribute

        Raises
        ------
        AttributeError
            Raised when trying to change the `tag` attribute
        SyntaxError
            Raised when trying to set the `text` attribute in 'NSDictionary' and
            'NSArray'
        ValueError
            Raised when trying to set the `text` attribute with a invalid type
            value that is not acceptable for the current 'PlistElement' object
        '''
        if attr == 'text' and not value in (None, ''):
            if isdirectory(self) or isbool(self):
                raise SyntaxError("`%s` cannot have a `text` attribute" % self.tag)

            elif self.tag in DEFAULT_KEY_IDS['date']:
                if not isinstance(value, (date, datetime)):
                    raise ValueError("`value` parameter must be `date` or\
 `datetime`, not `%s` when changing `text` attribute in a 'NSDate' object" % type(value))

                value = value.isoformat()

            elif self.tag in DEFAULT_KEY_IDS['int'] + DEFAULT_KEY_IDS['float']:
                if not isinstance(value, (int, float, str)):
                    raise ValueError("`value` parameter must be `int`, `float`\
or `str` number, not `%s` when changing `text` attribute on 'NSNumber' object" % type(value))
                try:
                    float(value)
                except ValueError:
                    raise ValueError('`%s` is not a valid `int` or `float`' % value)

                value = str(value)

            elif self.tag in DEFAULT_KEY_IDS['data']:
                if not isinstance(value, (bytearray, bytes)):
                    raise ValueError("`value` parameter must be `bytes` or\
 `bytearray`, not `%s` when changing `text` attribute on 'NSData' object" % type(value))

                value = b64encode(value).decode("ASCII")


        elif attr == 'tag':
            raise AttributeError('Cannot change the `tag` attribute. Replace\
 this element instead')
        super().__setattr__(attr, value)

    def __repr__(self) -> str:
        '''This method is called when trying to print a `PlistElement`.
        Returns a string that includes class name, tag and class id.'''

        return "<%s %r at %#x>" % (self.__class__.__name__, self.tag, id(self))

    def __len__(self) -> int:
        '''This instance is called on `len(PlistElement)`. It returns
        the number of sub-nodes in the `PlistElement`.'''

        return len(self._children)

    def __iter__(self) -> Generator[PlistElement, None, None]:
        '''This instance is being called when trying to iterate through a
        `PlistElement` in 'foreach' loops. It returns its sub-nodes if they
        exist.'''

        return (x for x in list.__iter__(self._children))

    def items(self) -> ItemsView[str, str]:
        '''Method copied from `xml.etree.ElementTree.Element` that is needed in
        a class for the `ElementTree.tostring` to work properly. It returns a
        'zip' that is being created from `self.attrib` keys and values.'''

        return self.attrib.items()

    def iter(self, tag: Optional[str] = None) -> Generator[PlistElement, None, None]:
        '''Method copied from `xml.etree.ElementTree.Element` that is needed in
        a class for the `ElementTree.tostring` to work properly. It iterates
        recursively on `PlistElement` sub-nodes if they exist.'''

        if tag == "*":
            tag = None
        if tag is None or self.tag == tag:
            yield self
        for e in self._children:
            yield from e.iter(tag)

    def __getitem__(self, index : Union[int, str]) -> Union[PlistElement]:
        '''`__getitem__` is called on `PlistElement[key]`. It returns a sub-node
        if it does exist.

        Parameters
        ----------
        index : Union[int, str]
                Key or index that is used to access a sub-node. If a `PlistElement`
                is a type of 'NSDictionary', `index` needs to be a string key. If
                a `PlistElement` is a type of 'NSArray', `index` needs to be
                a integer.

        Returns
        -------
        PlistElement
            Returns the target sub-node, if it was found in the sub-node list.

        Raises
        ------
        SyntaxError
            Raised when trying to access sub-nodes of a non directory
            `PlistElement`.
        ValueError
            Raised when trying to access to dict nodes by a integer, or when
            accessing array nodes by a string key. ValueError is also being
            raised when `index` parameter is not a type of `int` or `str`.
        IndexError
            Raised automatically when trying to access to sub-nodes in a
            'NSArray' by a integer index that is larger than the number of
            sub-nodes - 1.
        KeyError
            Raised automatically when trying to access to sub-nodes in a
            'NSDictionary' by a string key that does not exist in the dict.
        '''

        if not isdirectory(self):
            raise SyntaxError("PlistElement with tag `%s` can't have any nodes" % \
            self.tag)
        if isinstance(index, int):
            if self.tag in DEFAULT_KEY_IDS['dict']:
                raise ValueError("Can't access to dict nodes by a integer index")
            return self._children[index]
        elif isinstance(index, str):
            if self.tag in DEFAULT_KEY_IDS['array']:
                raise ValueError("Can't access to array nodes by a string key")
            # Get the index of `PlistElement` value that is linked by the string key
            # and return the target `PlistElement` from the subnode list by the index
            return self._children[self._dictitems[index]]
        else:
            raise ValueError("`index` is type of `%s`, not `str` or `int`" % type(index))

    def __setitem__(self, index : Union[int, str], value: PlistElement) -> None:
        '''`__setitem__` is called on `PlistElement[key] = PlistElement`
        It replaces an already setted `PlistElement` in a 'NSDictionary' and
        'NSArray'. If a key is not setted in a 'NSDictionary', it creates a new
        key and links the value to it. If you are trying to append new elements
        to a 'NSArray', use the `PlistElement.append` method instead.

        Parameters
        ----------
        index : Union[int, str]
            Key or index that is used to access the target sub-node which is
            going to be replaced later.
        value : PlistElement
            The element that is going to be assigned to the the target key/index.

        Raises
        ------
        SyntaxError
            Raised when trying to set a subnode in a non directory `PlistElement`
        ValueError
            Raised when trying to access to a sub-node in a 'NSDictionary' by a
            integer index, or when accessing a sub-node in 'NSArray' by a string
            key. ValueError is also being raised when `index` parameter is not a
            type of `int` or `str`.
        IndexError
            Raised automatically when trying to set a sub-node by a integer index
            in a 'NSArray', which is larger than the number of sub-nodes - 1.
        '''

        if not isdirectory(self):
            raise SyntaxError("PlistElement with tag `%s` cannot have any nodes")
        if isinstance(index, int):
            if self.tag in DEFAULT_KEY_IDS['dict']:
                raise ValueError("Cannot access to 'NSDictionary' nodes by int index")
            self._children[index] = value
        elif isinstance(index, str):
            if self.tag in DEFAULT_KEY_IDS['array']:
                raise ValueError("Cannot access to 'NSArray' nodes by a string key")
            try:
                self._children[self._dictitems[index]] = value
            except KeyError:
                # Create a 'NSKey' and append the value to it
                self._children.append(PlistElement(DEFAULT_KEY_IDS['key'][0], index))
                self._children.append(value)
                # Link the index of the value to the string key
                self._dictitems[index] = len(self._children) - 1
        else:
            raise ValueError("`index` input is a `%s`, not `int` or `str`" % type(index))

    def append(self, value: Union[PlistElement, List[PlistElement], Tuple[PlistElement]]) \
    -> None:
        '''Appends new `PlistElement` elements into a 'NSArray'. It cannot be
        used in a 'NSDictionary'.

        Parameters
        ----------
        value : Union[PlistElement, List[PlistElement], Tuple[PlistElement]]
            The value/values that are going to be appended to the current
            sub-node list. If trying to append multiple `PlistElement` elements,
            wrap them inside a tuple or a list.

        Raises
        ------
        SyntaxError
            Raised when trying to append elements to a non 'NSArray'
            `PlistElement`.
        ValueError
            Raised when `value` is not a type of `PlistElement`,
            `List[PlistElement]` or `Tuple[PlistElement]`
        '''

        if not self.tag in DEFAULT_KEY_IDS['array']:
            raise SyntaxError("Cannot append elements to a `%s` `PlistElement`" % self.tag)
        if not isinstance(value, (PlistElement, list, tuple)):
            # Simple type checking. I know that you can pass non PlistElement
            # in lists and tuples
            raise ValueError("`value` parameter is a type of `%s`, not `PlistElement`, \
`List[PlistElement]` or `Tuple[PlistElement]`" % type(value))
        if isinstance(value, PlistElement):
            # list.extend() can't add a single custom class (bug), so I wrap the
            # single element inside a list
            value = [value]
        self._children.extend(value)

    def pop(self, index: Union[int, str]) -> None:
        '''Deletes a sub-node in a 'NSArray'. In a 'NSDictionary' both the key
        and value is being deleted from the sub-node list.

        Parameters
        ----------
        index : Union[int, str]
            String key or integer index of the target sub-node that is going to
            be removed from the sub-node list.

        Raises
        ------
        ValueError
            Raised when trying to remove the target `PlistElement` by a string
            key in a 'NSArray' or when trying to remove the target element by a
            integer index in a 'NSDictionary'. ValueError is also raised when
            `index` parameter is not a type of `int` or `str`.
        IndexError
            Raised automatically when trying to delete a sub-node with an index
            that is larger than the number of sub-nodes - 1.
        '''

        if isinstance(index, int):
            if not self.tag in DEFAULT_KEY_IDS['array']:
                raise ValueError("Cannot delete a child by a integer index in a\
 `%s` `PlistElement`" % self.tag)
            del self._children[index]
        elif isinstance(index, str):
            if not self.tag in DEFAULT_KEY_IDS['dict']:
                raise ValueError("Cannot delete a dict value in a `%s`\
 PlistElement" % self.tag)
            # Delete the refered value
            del self._children[self._dictitems[index]]
            # Delete the key itself
            del self._children[self._dictitems[index] - 1]
            # Delete the infomation about the value index
            self._dictitems.pop(index)

        else:   raise ValueError('`index` input is not a `int` or `str`')