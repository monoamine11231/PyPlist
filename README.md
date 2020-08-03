# PyPlist - A Python3 library for XML property lists
'PyPlist' is a compact library based on `xml.etree.ElementTree` module for
parsing and modifying standard and non-standard
[XML property lists](https://developer.apple.com/library/archive/documentation/General/Conceptual/DevPedia-CocoaCore/PropertyList.html).

Apple's XML property list format is using XML to store and represent
dictionaries, arrays and values with a fixed data-type. The property list format
supports integers, floats, strings, date (ISO-format), boolean values,
binary data (encoded in base64), dictionaries and arrays.

## Requirements
This library is using the `typing` module, and therefore **python 3.5** and
higher is required. If Python's standard packages are not installed, `xml.etree`
package needs to be installed manually for this library to work.

## Installation
```console
user@linux:~/tmpfolder$ git clone https://github.com/monoamine11231/PyPlist/
user@linux:~/tmpfolder$ cd PyPlist
user@linux:~/tmpfolder/PyPlist$ pip3 install .
```

## Quick overlook
`pyplist.tree.PlistElement` is a node class that is used to edit the current node and sub-nodes.

**pyplist.tree.PlistElement**<br/>
When initializing a new `pyplist.tree.PlistElement` object, a tag name that has been defined
in the current tag namespace and a inner-text is required. If the tag name is
associated with 'NSDictionary', 'NSArray' or 'NSBool', the `text` parameter must
be empty.

```python
from pyplist.tree import PlistElement

# Value element
element: PlistElement = PlistElement('real', 2.2)

# Directory element
element: PlistElement = PlistElement('dict')
```
***
To add keys and values in a 'NSDictionary', the key operator is used.

```python
# Creating a 'NSDictionary' object
element: PlistElement = PlistElement('dict')
# Adding a key and linking the value to it
element['mykey'] = PlistElement('true')
```
***
To append element/elements into a 'NSArray', the `PlistElement.append` method
is used. Note that `PlistElement.append` is working only on 'NSArray'
objects.

```python
# Creating a 'NSArray'
element: PlistElement = PlistElement('array')
# Appending a single element
element.append(PlistElement('date', datetime.date.today()))
# Appending multiple elements
element.append([PlistElement('string', 'some string'), PlistElement('false')])
```
***
<br/>

**Parsing**<br/>
Note that all parsing methods return a root `PlistElement` object that contain
the whole tree; `<plist>` tag is being discarded.<br/><br/>
To parse a file, `pyplist.convert.fromfile` method is used, as shown in the example bellow.<br/>
```python
from pyplist.tree import PlistElement
from pyplist.convert import fromfile, fromstring, fromdict

element: PlistElement = fromfile('file.plist')
```
***
To parse a string, `pyplist.convert.fromstring` method is used, as shown in the example bellow.<br/>
```python
element: PlistElement = fromstring(your_string)
```
***
To parse a dict/list, `pyplist.convert.fromdict` method is being used. Note that date strings
are being interpreted as strings and not 'NSDate' objects.<br/>
```python
element: PlistElement = fromdict({'key': 'string'})
```
***
<br/>

**Converting to different types**<br/>
A property list tree can be converted to string using `pyplist.convert.tostring` method, and to
dict/list using `pyplist.convert.todict` method. Note that `pyplist.convert.todict` method ignores inner-tag
arguments.<br/><br/>

**Tag namespaces**<br/>
This library can be used to parse and modify standard and non-standard XML
property lists. Non-standard XML property lists are lists that use non-standard
tag names for different objects. Standard tag names for different property list
objects can be seen [here](https://developer.apple.com/library/archive/documentation/General/Conceptual/DevPedia-CocoaCore/PropertyList.html).

One or multiple tags can be associated with the same plist object by using
`pyplist.namespace.updatekeys` method; `pyplist.namespace.updatekeys` takes in a namespace dictionary that contain
the new tag definitions.

Namespace dictionaries use the format shown bellow.
```python
{
    'key' : [init_tag, alias1, alias2, ...], 'string' : [init_tag, alias1, alias2, ...],
    'data' : [init_tag, alias1, alias2, ...], 'dict' : [init_tag, alias1, alias2, ...],
    'array' : [init_tag, alias1, alias2, ...], 'int' : [init_tag, alias1, alias2, ...],
    'true' : [init_tag, alias1, alias2, ...], 'false' : [init_tag, alias1, alias2, ...],
    'float' : [init_tag, alias1, alias2, ...], 'date' : [init_tag, alias1, alias2, ...]
}
```

`init_tag` is the first tag in the definition list that is being used when
creating new `pyplist.tree.PlistElement` objects inside methods that cannot be controlled by
the user. Such methods is `__setitem__` in 'NSDictionary' objects, where a
'NSKey' is being created automatically with the `init_tag`.

`alias1`, `alias2`, `...` are different tag names associated with the same plist
object.



## Notes
 - `pyplist.convert.todict` method ignores inner-tag arguments.
 - This library ignores inner text between two opening tags and between two
 ending tags.
 - In version '0.0.1', the `<plist>` tag is being discarded.
 - When parsing non-standard plist files or strings, the new tag aliases must be
  defined using `pyplist.namespace.updatekeys` method.

## Changelog
 - 0.0.1 - Released

## Credits
This library extends, uses and modifies the `xml.etree.ElementTree` module.
According to module's licensing rules, the following notice must be included
in this documentation:
***

The ElementTree toolkit is<br/>
Copyright (c) 1999-2008 by Fredrik Lundh<br/>
[fredrik@pythonware.com](mailto:fredrik@pythonware.com)<br/>
[http://www.pythonware.com](http://www.pythonware.com)


By obtaining, using, and/or copying this software and/or its
associated documentation, you agree that you have read, understood,
and will comply with the following terms and conditions:

Permission to use, copy, modify, and distribute this software and
its associated documentation for any purpose and without fee is
hereby granted, provided that the above copyright notice appears in
all copies, and that both that copyright notice and this permission
notice appear in supporting documentation, and that the name of
Secret Labs AB or the author not be used in advertising or publicity
pertaining to distribution of the software without specific, written
prior permission.

SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANT-
ABILITY AND FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR
BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
OF THIS SOFTWARE.

## License
This library is using the [Boost Software License 1.0](https://www.boost.org/LICENSE_1_0.txt)