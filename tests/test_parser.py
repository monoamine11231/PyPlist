# type: ignore
import pytest
import src.parser, src.tree, src.namespace
from datetime import date


def test__dicterror() -> None:
    with pytest.raises(ValueError):
        src.parser._dicterror(src.tree.PlistElement('key'))
    # Empty dict without sub-nodes should return `False`
    assert(not src.parser._dicterror(src.tree.PlistElement('dict')))

    # Create a dict with odd amount of sub-nodes
    test_dict: src.tree.PlistElement = src.tree.PlistElement('dict')
    test_dict._children.append(src.tree.PlistElement('key', 'test_key'))
    assert(src.parser._dicterror(test_dict))
    # The linked value cannot be a key element
    test_dict._children.append(src.tree.PlistElement('key', 'linked_value'))
    assert(src.parser._dicterror(test_dict))
    # The key element must be a 'NSKey'
    test_dict._children[0] = src.tree.PlistElement('true')
    assert(src.parser._dicterror(test_dict))

def test__dictattrstoxml() -> None:
    assert(src.parser._dictattrstoxml({}) == '')
    assert(src.parser._dictattrstoxml({'abc' : "'test", 'def': 'ab"c'})
        == ' abc="\'test" def="ab\\\"c"')


def test_PlistXML_init() -> None:
    test_init: src.parser.PlistXML = src.parser.PlistXML()
    assert(not test_init._parser == None)
    assert(not test_init._orderelementlist == None)

def test_PlistXML_parse() -> None:
    test_plist: str = '''<plist><dict><key>k1</key><int>2</int></dict></plist>'''
    with pytest.raises(SyntaxError):
        src.parser.PlistXML().parse('invalid_plist_xml')
    root: src.tree.PlistElement = src.parser.PlistXML().parse(test_plist)
    assert(root.tag == 'dict')
    assert(root['k1'].tag == 'int' and root['k1'].text == '2')

def test_PlistXML_parsefile() -> None:
    with pytest.raises(SyntaxError):
        src.parser.PlistXML().parsefile('tests/unvalid_plist')
    root: src.tree.PlistElement = src.parser.PlistXML().parsefile('tests/valid_plist')
    assert(root.tag == 'dict' and root['a'][2].text == '2012-01-02')

def test_PlistXML__start() -> None:
    parser: src.parser.PlistXML = src.parser.PlistXML()
    parser._start('plist', {})
    # Check if `plist` object is being ignored
    assert(parser._orderelementlist == [])

    parser._start('dict', {'one': '1'})
    # Check if attributes and tag name are being passed to the PlistElement object
    assert(parser._orderelementlist[0].tag == 'dict' \
        and parser._orderelementlist[0].attrib == {'one': '1'})

def test_PlistXML__end() -> None:
    with pytest.raises(SyntaxError):
        parser: src.parser.PlistXML = src.parser.PlistXML()
        # Create a unvalid 'NSDictionary' with a single unlinked key
        unvalid_dict: src.tree.PlistElement = src.tree.PlistElement('dict')
        unvalid_dict._children.append(src.tree.PlistElement('key', 'test'))
        parser._orderelementlist.append(unvalid_dict)
        parser._validate_dicts = True
        parser._end('dict')

    parser: src.parser.PlistXML = src.parser.PlistXML()
    parser._validate_dicts = True
    # Create a 'NSDictionary' and fill it
    target: src.tree.PlistElement = src.tree.PlistElement('dict')
    target['k1'] = src.tree.PlistElement('integer', 2)
    parser._orderelementlist.append(target)
    parser._end('dict')
    # See if there are changes to the root object. `_end` method should not
    # change the root object if it is the only element in the ordered list.
    assert(parser._orderelementlist[-1] == target)

    parser._orderelementlist.append(src.tree.PlistElement('key', 'empty_key'))
    parser._end('key')
    # Check if the linked value index of the `empty_key` is one larger than the
    # index of the actual 'NSKey' element
    assert(parser._orderelementlist[-1]._dictitems['empty_key'] == 3)

def test_PlistXML__data() -> None:
    with pytest.raises(ValueError):
        parser: src.parser.PlistXML = src.parser.PlistXML()
        unvalid_data: src.tree.PlistElement = src.tree.PlistElement('data', parsedobj=True)
        parser._orderelementlist.append(unvalid_data)
        parser._data('not_valid_base64')

    parser: src.parser.PlistXML = src.parser.PlistXML()
    # Test 'NSDate' objects
    parser._orderelementlist.append(src.tree.PlistElement('date', parsedobj=True))
    parser._data('2012-01-02')
    assert(parser._orderelementlist[0].text == '2012-01-02')
    # Test 'NSData' objects
    parser._orderelementlist[0] = src.tree.PlistElement('data', parsedobj=True)
    parser._data('dGVzdF9zdHJpbmc=')
    assert(parser._orderelementlist[0].text == 'dGVzdF9zdHJpbmc=')
    # Test non-'NSData' and non-'NSDate' objects
    parser._orderelementlist[0] = src.tree.PlistElement('integer', parsedobj=True)
    parser._data('2')
    assert(parser._orderelementlist[0].text == '2')
