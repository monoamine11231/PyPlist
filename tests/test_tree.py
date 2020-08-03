# type: ignore

import pytest
import src.tree
import datetime
from collections import abc

def test_dateobj() -> None:
    datettime_str: str = '2020-07-26T21:27:49.012728'
    date_str: str = '2020-07-26'

    assert(type(src.tree.dateobj(datettime_str)) == datetime.datetime)
    assert(type(src.tree.dateobj(date_str)) == datetime.date)

def test_isbool() -> None:
    assert(src.tree.isbool(src.tree.PlistElement('true')))
    assert(src.tree.isbool(src.tree.PlistElement('false')))
    assert(not src.tree.isbool(src.tree.PlistElement('key', 'test')))

def test_isdirectory() -> None:
    assert(src.tree.isdirectory(src.tree.PlistElement('dict')))
    assert(src.tree.isdirectory(src.tree.PlistElement('array')))
    assert(not src.tree.isdirectory(src.tree.PlistElement('true')))


def test_PlistElement_init() -> None:
    with pytest.raises(ValueError):
        src.tree.PlistElement('non_existing_tag')
    with pytest.raises(ValueError):
        src.tree.PlistElement('key', 'text', bytearray(12))

    assert(src.tree.PlistElement('dict').tag == 'dict')
    assert(src.tree.PlistElement('key', 'test_text', parsedobj=True).text
        == '')

def test_PlistElement_setattr() -> None:
    dict_element: src.tree.PlistElement = src.tree.PlistElement('dict')
    true_element: src.tree.PlistElement = src.tree.PlistElement('true')
    with pytest.raises(SyntaxError):
        dict_element.text = 'test_value'
        true_element.text = 'test_value'
    # Should not raise any errors if the value is a empty string
    dict_element.text = ''
    true_element.text = ''

    # PlistElement.__init__ calls __setattr__ method
    # NSDate
    date_element: src.tree.PlistElement = src.tree.PlistElement('date', datetime.date.today())
    with pytest.raises(ValueError):
        date_element.text = 'not_a_datetime.date_obj'

    date_element.text = datetime.date(2020, 1, 1)
    assert(date_element.text == '2020-01-01')

    date_element.text = datetime.datetime(2020, 1, 1, 1, 1, 1, 1)
    assert(date_element.text == '2020-01-01T01:01:01.000001')

    # NSNumber
    float_element: src.tree.PlistElement = src.tree.PlistElement('real', 12.1)
    with pytest.raises(ValueError):
        float_element.text = 'not_a_string_number'

    # Coverage.py bug that doesn't detect two syntax errors in one `pytest.raises`
    # scope.
    with pytest.raises(ValueError):
        float_element.text = bytearray(1)
    float_element.text = '12'
    assert(float_element.text == '12')

    # NSData
    data_element: src.tree.PlistElement = src.tree.PlistElement('data', b'test_bytes')
    with pytest.raises(ValueError):
        data_element.text = 'simple_string_and_not_bytes'
    data_element.text = b'test_bytes'
    assert(data_element.text == 'dGVzdF9ieXRlcw==')

    # Check if trying to change the tag
    with pytest.raises(AttributeError):
        src.tree.PlistElement('dict').tag = 'key'

def test_PlistElement_repr() -> None:
    assert(src.tree.PlistElement('true').__repr__().index('<PlistElement') == 0)

def test_PlistElement_len() -> None:
    assert(len(src.tree.PlistElement('array')) == 0)

def test_PlistElement__iter_() -> None:
    assert(issubclass(type(src.tree.PlistElement('dict').__iter__()), abc.Generator))

def test_PlistElement_items() -> None:
    assert(issubclass(type(src.tree.PlistElement('dict').items()), abc.ItemsView))

def test_PlistElement_iter() -> None:
    test_element: src.tree.PlistElement = src.tree.PlistElement('array')
    assert(list(test_element.iter('*')) == [test_element])
    assert(list(test_element.iter()) == [test_element])

    # PlistElement.append() should be used. This is for unit testing purposes only
    appended_element: src.tree.PlistElement = src.tree.PlistElement('key', 'test')
    test_element._children.append(appended_element)
    assert(list(test_element.iter('key')) == [appended_element])

def test_PlistElement_getitem() -> None:
    append_element1: src.tree.PlistElement = src.tree.PlistElement('true')
    append_element2: src.tree.PlistElement = src.tree.PlistElement('false')
    array_element: src.tree.PlistElement = src.tree.PlistElement('array')
    dict_element: src.tree.PlistElement = src.tree.PlistElement('dict')

    # `PlistElement.append(element)` must be used instead. This is done just for
    # unit testing purposes
    array_element._children.append(append_element1)
    # `PlistElement['key'] = element` must be used instead. This is done just for
    # unit testing purposes
    dict_element['test'] = append_element2

    with pytest.raises(SyntaxError):
        src.tree.PlistElement('key')[0]
    with pytest.raises(ValueError):
        dict_element[0]
    with pytest.raises(ValueError):
        array_element['key']
    assert(array_element[0] == append_element1)
    assert(dict_element['test'] == append_element2)

    with pytest.raises(ValueError):
        array_element[bytearray(1)]

def test_PlistElement_setitem() -> None:
    append_element1: src.tree.PlistElement = src.tree.PlistElement('true')
    append_element2: src.tree.PlistElement = src.tree.PlistElement('false')
    array_element: src.tree.PlistElement = src.tree.PlistElement('array')
    dict_element: src.tree.PlistElement = src.tree.PlistElement('dict')
    # `PlistElement.append(element)` must be used instead. This is done just for
    # unit testing purposes
    array_element._children.append(append_element1)

    with pytest.raises(SyntaxError):
        src.tree.PlistElement('key', 'test')[0] = None
    with pytest.raises(ValueError):
        dict_element[0] = None
    with pytest.raises(ValueError):
        array_element['key'] = None
    array_element[0] = append_element2
    assert(array_element._children[0] == append_element2)

    dict_element['key1'] = append_element2
    assert(dict_element._children[0].tag == 'key')
    assert(dict_element._children[1] == append_element2)
    # Key name needs to point to the value index in the ordered list
    assert(dict_element._dictitems['key1'] == 1)

    with pytest.raises(ValueError):
        array_element[bytearray(1)] = append_element1

def test_PlistElement_append() -> None:
    array_element: src.tree.PlistElement = src.tree.PlistElement('array')
    append_element: src.tree.PlistElement = src.tree.PlistElement('true')
    with pytest.raises(SyntaxError):
        src.tree.PlistElement('dict').append(None)
    with pytest.raises(ValueError):
        array_element.append(None)
    array_element.append(append_element)
    assert(array_element._children[0] == append_element)

def test_PlistElement_pop() -> None:
    append_element1: src.tree.PlistElement = src.tree.PlistElement('true')
    append_element2: src.tree.PlistElement = src.tree.PlistElement('false')
    dict_element: src.tree.PlistElement = src.tree.PlistElement('dict')
    array_element: src.tree.PlistElement = src.tree.PlistElement('array')

    with pytest.raises(ValueError):
        dict_element.pop(0)
    array_element._children.append(append_element1)
    array_element.pop(0)
    assert(array_element._children == [])

    with pytest.raises(ValueError):
        array_element.pop('key')
    key_element: src.tree.PlistElement = src.tree.PlistElement('key', 'test')
    dict_element['test'] = key_element
    dict_element.pop('test')
    assert(not append_element2 in dict_element._children)
    assert(not key_element in dict_element._children)
    assert(not 'test' in dict_element._dictitems)

    with pytest.raises(ValueError):
        array_element.pop(bytearray(1))
