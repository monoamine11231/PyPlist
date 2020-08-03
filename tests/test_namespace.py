import src.namespace

def test_updatekeys() -> None:
    src.namespace.updatekeys({'int': ['intager', 'integer', 'int']})
    assert(src.namespace.DEFAULT_KEY_IDS['int'] == ['intager', 'integer', 'int'])
    assert('intager' in src.namespace.DEFAULT_KEYS)
    assert('int' in src.namespace.DEFAULT_KEYS)
    # Test if non affected keys have been changed in some way
    assert('key' in src.namespace.DEFAULT_KEY_IDS['key'])