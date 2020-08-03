# type: ignore
import pytest
import src.convert, src.tree
from datetime import date


def test_fromstring() -> None:
    root: src.tree.PlistElement = src.convert.fromstring(
        '<dict><key>2</key><array><integer>5</integer><string>test</string></array></dict>')
    assert(root['2'][1].text == 'test' and root['2'][1].tag == 'string')

def test_fromfile() -> None:
    root: src.tree.PlistElement = src.convert.fromfile('tests/valid_plist')
    assert(root['a'][2].tag == 'date' and root['a'][2].text == '2012-01-02')

def test_todict() -> None:
    root: src.tree.PlistElement = src.tree.PlistElement('dict')
    with pytest.raises(AssertionError):
        # PlistElement[key] = value, should be used instead
        # ... creating a unvalid 'NSDictionary'
        root._children.append(src.tree.PlistElement('key', 'test_key1'))
        src.convert.todict(root)
    # Make the unvalid 'NSKey' valid
    root._children.append(src.tree.PlistElement('integer', 1))
    root._dictitems['test_key1'] = len(root._children) - 1

    # Fill with test values
    root['test_key2'] = src.tree.PlistElement('real', 1.2)
    root['test_key3'] = src.tree.PlistElement('date', date.today())
    root['test_key4'] = src.tree.PlistElement('true')

    # Filling a 'NSArray'
    node: src.tree.PlistElement = src.tree.PlistElement('array')
    node.append(src.tree.PlistElement('false'))
    node.append(src.tree.PlistElement('data', b'some_text'))
    node.append(src.tree.PlistElement('integer', 0))
    node.append(src.tree.PlistElement('real', 0.1))
    node.append(src.tree.PlistElement('string', 'test_string'))
    node.append(src.tree.PlistElement('dict'))
    root['test_key5'] = node

    root['test_key6'] = src.tree.PlistElement('string', 'test_string')
    root['test_key7'] = src.tree.PlistElement('data', b'some_text')

    dicted = src.convert.todict(root, decode_data = True)

    # Test if everything works
    assert(dicted['test_key1'] == 1)
    assert(dicted['test_key2'] == 1.2)
    assert(dicted['test_key3'] == date.today())
    assert(dicted['test_key4'])
    assert(not dicted['test_key5'][0])
    assert(dicted['test_key5'][1] == b'some_text')
    assert(dicted['test_key5'][2] == 0)
    assert(dicted['test_key5'][3] == 0.1)
    assert(dicted['test_key5'][4] == 'test_string')
    assert(dicted['test_key5'][5] == {})

    assert(dicted['test_key6'] == 'test_string')
    assert(dicted['test_key7'] == b'some_text')
    assert(src.convert.todict(
        src.tree.PlistElement('string', 'some_text')) == ['some_text']
    )

def test_tostring() -> None:
    test_element: src.tree.PlistElement = src.tree.PlistElement('dict')
    test_element['test_key1'] = src.tree.PlistElement('integer', 3)
    test_element['test_key2'] = src.tree.PlistElement('string', 'somestring')

    conv: str = '<dict><key>test_key1</key><integer>3</integer><key>test_key2</key><string>somestring</string></dict></plist>'
    ver: str = src.convert.tostring(test_element, xml_declaration = 'ver')
    enc_attr: str = src.convert.tostring(test_element, plist_attrs = {'yes': 'no', 'one': '1'}, xml_declaration = 'enc')

    assert(ver == ('<?xml version="1.0"?><plist>' + conv))
    assert(enc_attr == ('<?xml version="1.0" encoding="UTF-8"?><plist yes="no" one="1">' + conv))

def test_fromdict() -> None:
    source_dict: dict = {
        'test_key1': 2, 'test_key2': 2.1, 'test_key3': 'string',
        'test_key4': date.today(), 'test_key5': True, 'test_key6': b'some_text',
        'test_key7': [0, 'text']
    }
    source_list: list = [
        0, 0.1, 'test-text', date(2000, 1, 1), False, bytearray(b'\x00\x01\x02'),
        {'test_key1': True}
    ]

    plist_dict: src.tree.PlistElement = src.convert.fromdict(source_dict)
    plist_list: src.tree.PlistElement = src.convert.fromdict(source_list)

    # Test dict parsing
    assert(plist_dict['test_key1'].text == '2' and plist_dict['test_key1'].tag == 'integer')
    assert(plist_dict['test_key2'].text == '2.1' and plist_dict['test_key2'].tag == 'real')
    assert(plist_dict['test_key3'].text == 'string' and plist_dict['test_key3'].tag == 'string')
    assert(plist_dict['test_key4'].text == date.today().isoformat() and plist_dict['test_key4'].tag == 'date')
    assert(plist_dict['test_key5'].tag == 'true')
    assert(plist_dict['test_key6'].text == 'c29tZV90ZXh0' and plist_dict['test_key6'].tag == 'data')
    assert(plist_dict['test_key7'][0].text == '0' and plist_dict['test_key7'][0].tag == 'integer')

    # Test array parsing
    assert(plist_list[0].text == '0' and plist_list[0].tag == 'integer')
    assert(plist_list[1].text == '0.1' and plist_list[1].tag == 'real')
    assert(plist_list[2].text == 'test-text' and plist_list[2].tag == 'string')
    assert(plist_list[3].text == '2000-01-01' and plist_list[3].tag == 'date')
    assert(plist_list[4].tag == 'false')
    assert(plist_list[5].text == 'AAEC' and plist_list[5].tag == 'data')
    assert(plist_list[6]['test_key1'].tag == 'true')

    # Test exceptions
    with pytest.raises(ValueError):
        src.convert.fromdict({'test_key1': None})

    with pytest.raises(ValueError):
        src.convert.fromdict([None])

    with pytest.raises(ValueError):
        src.convert.fromdict(None)
