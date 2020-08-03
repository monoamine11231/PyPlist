from typing import Union, Dict, List, no_type_check
from xml.etree.ElementTree import ParseError, tostring as etree_tostring
from datetime import date, datetime
from base64 import b64decode

from . import APTypes
from .tree import PlistElement, dateobj, isdirectory, isbool
from .parser import PlistXML, _dicterror, _dictattrstoxml
from .namespace import *


def fromstring(string: str, validate_dicts: bool = True) -> PlistElement:
    '''Parses a string and converts it to a constructed `PlistElement` element

    Parameters
    ----------
    string : str
        Source xml/plist string that is going to be parsed
    validate_dicts : bool = True
        Indicates if parsed 'NSDictionary' elements are going to be validated
        with `_dicterror` method. Setting this variable to `False` makes this
        method faster by ignoring the validation of 'NSDictionary' elements.

    Returns
    -------
    PlistElement
        When source string was successfully read and parsed by `expat`.

    Raises
    ------
    SyntaxError
        Raised when `string` parameter contains invalid 'xml'.
    '''

    return PlistXML().parse(string, validate_dicts)

def fromfile(filename: str, validate_dicts: bool = True) -> PlistElement:
    '''Reads a file and parses the file contents to an `PlistElement`

    Parameters
    ----------
    filename : str
        Path to the file that is going to be parsed.
    validate_dicts : bool = True
        Indicates if parsed 'NSDictionary' elements are going to be validated
        with `_dicterror` method. Setting this variable to `False` makes this
        method faster by ignoring the validation of 'NSDictionary' elements.

    Returns
    -------
    PlistElement
        When file contents were successfully read and parsed by `expat`.

    Raises
    ------
    SyntaxError
        Raised if the target file contains invalid 'xml'.
    '''

    return PlistXML().parsefile(filename, validate_dicts)


# To be removed when `mypy` implements recursive types
@no_type_check
def todict(element: PlistElement, validate_dicts: bool=True,\
    decode_data: bool=False) -> Union[Dict[str, APTypes], List[APTypes]]:
    '''Reads a `PlistElement` tree and converts it to a `list`/`dict`.
    The attributes inside 'PlistElement' objects are being discarded.

    Parameters
    ----------
    element : PlistElement
        Target `PlistElement` element that is going to be read and converted
        to a `dict`/`list`
    validate_dicts : bool = True
        Indicates if 'NSDictionary' elements are going to be validated
        with `_dicterror` method. Setting this variable to `False` makes this
        method faster by ignoring the validation of 'NSDictionary' elements.
    decode_data : bool = False
        Indicates if base64 strings from 'NSData' objects are going to be
        decoded or not.

    Returns
    -------
    Dict[str, APTypes]
        Returned when `element` parameter was successfully read, parsed and
        the root element was a 'NSDictionary'.
    List[APTypes]
        Returned when `element` parameter was successfully read, parsed and
        the root element was a 'NSArray', 'NSNumber', 'NSDate', 'NSString',
        'NSBool' or 'NSData'. Flat 'plist' objects are being wrapped inside an
        empty list.

    Raises
    ------
    AssertionError
        Raised when `validate_dicts` parameter is set to `True` and a invalid
        'NSDictionary' was detected
    '''

    # Root element of the `dict`/`list` tree
    root: Union[Dict[str, APTypes], List[APTypes]]
    if element.tag in DEFAULT_KEY_IDS['dict']:
        # Check if the 'NSDictionary' is valid if the user choosed to check the
        # 'NSDictionary' elements
        if validate_dicts: assert(not _dicterror(element))
        root = {}
        # Keys are followed by linked values in `PlistElement` subnode lists
        keys: List[PlistElement] = element._children[::2]
        values: List[PlistElement] = element._children[1::2]
        # Join two elements with same index from `keys` and `values` lists into
        # tuples and iterate through them
        for k, v in zip(keys, values):
            # If the linked value is a dict or a list, parse it and link the
            # result to the key
            if isdirectory(v):
                root[k.text] = todict(v, validate_dicts, decode_data)
            # Else link the key to the value
            elif decode_data and v.tag in DEFAULT_KEY_IDS['data']:
                root[k.text] = b64decode(v.text)
            elif v.tag in DEFAULT_KEY_IDS['int']:   root[k.text] = int(v.text)
            elif v.tag in DEFAULT_KEY_IDS['float']: root[k.text] = float(v.text)
            elif v.tag in DEFAULT_KEY_IDS['date']:  root[k.text] = dateobj(v.text)
            elif isbool(v):
                root[k.text] = True if v.tag in DEFAULT_KEY_IDS['true'] else False
            else:                                   root[k.text] = v.text
        # Return the constructed dict
        return root
    elif element.tag in DEFAULT_KEY_IDS['array']:
        root = []
        for e in element._children:
            if isdirectory(e):
                root.append(todict(e, validate_dicts, decode_data))
            elif decode_data and e.tag in DEFAULT_KEY_IDS['data']:
                root.append(b64decode(e.text))
            elif e.tag in DEFAULT_KEY_IDS['int']:   root.append(int(e.text))
            elif e.tag in DEFAULT_KEY_IDS['float']: root.append(float(e.text))
            elif e.tag in DEFAULT_KEY_IDS['date']:  root.append(dateobj(e.text))
            elif isbool(e):
                root.append(True if e.tag in DEFAULT_KEY_IDS['true'] else False)
            else:                                   root.append(e.text)
        # Return the constructed list
        return root
    # If the element is not a directory 'plist' element, wrap it inside an
    # empty list
    else:   return [element.text]

def tostring(element: PlistElement, plist_attrs: Dict[str, str] = {},\
    xml_declaration: str = '', short_empty_elements: bool = True) -> str:
    '''Reads a `PlistElement` and converts it to a string.

    Parameters
    ----------
    element : PlistElement
        The target element that is going to be readed
    plist_attrs : Dict[str, str] = {}
        'xml' attributes that are going to be added inside the '<plist>' tag
    xml_declaration : str = ''
        When `xml_declaration` is '', no declaration is being added to the
        beginning of the string. If `xml_declaration` is 'ver', the added
        declaration is '<?xml version="1.0"?>' and if `xml_declaration` is 'enc',
        the added declaration is '<?xml version="1.0" encoding="UTF-8"?>'
    short_empty_elements : bool = True
        If `short_empty_elements` is `True`, 'NSBool' elements are going to be
        parsed like this: '<X/>'. If `short_empty_elements` is `False`, 'NSBool'
        elements are going to be parsed in the following way: '<X></X>'

    Returns
    -------
    str
        Raised when target `PlistElement` element was readed and parsed
        successfully.
    '''

    plist_header: str = '<plist%s>' % _dictattrstoxml(plist_attrs)
    # Note that `# type: ignore` is being used bellow to ignore warnings that
    # are being caused because of duck-typing
    raw_content: str = etree_tostring(element, encoding='unicode',
        short_empty_elements=short_empty_elements) # type: ignore
    declaration: str = ''
    if xml_declaration == 'ver':
        declaration = '<?xml version="1.0"?>'
    elif xml_declaration == 'enc':
        declaration = '<?xml version="1.0" encoding="UTF-8"?>'
    # Build the final string
    return '%s%s%s</plist>' % (declaration, plist_header, raw_content)

# To be removed when `mypy` implements recursive types
@no_type_check
def fromdict(source: Union[Dict[str, APTypes], List[APTypes]]) -> PlistElement:
    '''Parses a dict or a list to a `PlistElement`

    Parameters
    ----------
    source : Union[Dict[str, _this_], List[_this_]]
        The target dict or list that is going to be parsed

    Returns
    -------
    PlistElement
        When the target dict or list has been parsed successfully

    Raises
    ------
    ValueError
        Raised automatically when a key in `source` dict is not a string.
        ValueError is also raised when a value in `source` dict/list is not a
        `dict`, `list`, `int`, `str`, `bytes` or `bytearray`. ValueError is
        raised if `source` parameter is not a `dict` or a `list`.

    '''

    root: PlistElement
    if isinstance(source, dict):
        # Define root element as a 'NSDictionary' if `source` is a `dict`
        root = PlistElement(DEFAULT_KEY_IDS['dict'][0])
        for k,v in source.items():
            # If the value is a `dict` or a `list`, parse it and link the
            # result to the target key
            if isinstance(v, (list, dict)): root[k] = fromdict(v)
            elif isinstance(v, bool):
                root[k] = PlistElement(
                    DEFAULT_KEY_IDS['true' if v else 'false'][0])
            # Link python type to 'plist' type tag definitions
            elif isinstance(v, (int, float, str, bytes, bytearray, date, datetime)):
                root[k] = PlistElement(
                    DEFAULT_KEY_IDS[TYPE_TO_KEYNAME[type(v)]][0], v)
            else: raise ValueError('`v` is a `%s`, not `dict`, `list`, `int`, \
`str`, `bytes`, `bytearray`, `datetime.date` or `datetime.datetme`' % v)
        # Return the fully constructed `PlistElement`
        return root
    elif isinstance(source, list):
        # Define root element as a 'NSArray' if `source` parameter is a `list`
        root = PlistElement(DEFAULT_KEY_IDS['array'][0])
        for v in source:
            # If the value is a `dict` or a `list`, parse it, and append the
            # result to the root 'NSArray' element
            if isinstance(v, (list, dict)): root.append(fromdict(v))
            elif isinstance(v, bool):
                root.append(PlistElement(
                    DEFAULT_KEY_IDS['true' if v else 'false'][0]))
            # Link python type to 'plist' type tag definitions
            elif isinstance(v, (int, float, str, bytes, bytearray, date, datetime)):
                root.append(PlistElement(
                    DEFAULT_KEY_IDS[TYPE_TO_KEYNAME[type(v)]][0], v))
            else: raise ValueError('`v` is `%s`, not `dict`, `list`, `int`, \
 `str`, `bytes`, `bytearray`, `datetime.date` or `datetime.datetme`' % v)
        # Return the fully constructed `PlistElement`
        return root
    else: raise ValueError('`source` parameter is not a `dict` or a `list`')