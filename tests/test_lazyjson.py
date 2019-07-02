# -*- encoding: utf-8

import json

from storage import lazyjson


def test_gets_value(tmpdir):
    path = tmpdir.join("data.json")
    path.write('{"hello": "world"}')
    assert lazyjson.LazyJsonObject(path).read() == {"hello": "world"}


def test_caches_value(tmpdir):
    def count_open(*args, **kwargs):
        count_open.called += 1
        return open(*args, **kwargs)

    count_open.called = 0
    lazyjson.open = count_open

    path = tmpdir.join("data.json")
    path.write('{"hello": "world"}')
    lazy_object = lazyjson.LazyJsonObject(path)

    for _ in range(5):
        lazy_object.read()

    assert count_open.called == 1


def test_gets_updated_value(tmpdir):
    path = tmpdir.join("data.json")
    path.write('{"hello": "world"}')
    lazy_object = lazyjson.LazyJsonObject(path)
    assert lazy_object.read() == {"hello": "world"}

    path.write('{"name": "lexie"}')
    assert lazy_object.read() == {"name": "lexie"}


def test_can_write_value(tmpdir):
    path = tmpdir.join("data.json")
    path.write('{"hello": "world"}')
    lazy_object = lazyjson.LazyJsonObject(path)

    lazy_object.write({"name": "lexie"})
    assert lazy_object.read() == {"name": "lexie"}
    assert json.load(open(path)) == {"name": "lexie"}
