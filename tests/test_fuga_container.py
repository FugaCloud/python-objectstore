from io import BytesIO
from types import SimpleNamespace

import pytest

from fuga_object_store import FugaConnection, FugaContainer, FugaObjectStore


class MockConnectionReturnValue(object):

    def __init__(self, listvalue=None, name=None):
        if name is None:
            self.name = 'test'
        else:
            self.name = name
        self.listvalue = listvalue
        self.connection = MockKey("")

    def list(self):
        return self.listvalue

    def get_key(self, *args, **kwargs):
        if args[0] not in [x.name for x in self.listvalue]:
            return None
        return MockKey(args[0])

    def new_key(self, *args, **kwargs):
        return MockKey(args[0])

    def __repr__(self):
        return '<MockConnection {}>'.format(self.name)


class MockKey(object):

    def __init__(self, value):
        self.name = value
        self.filename = value

    def delete(self):
        pass

    def get_contents_as_string(self):
        return bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    def set_contents_from_file(self, *args, **kwargs):
        pass

    def close(self):
        pass


@pytest.fixture
def connecting_s3():
    return_object = SimpleNamespace()
    return_object.get_bucket = lambda name: MockConnectionReturnValue(
        listvalue=[MockKey('1'), MockKey('2'), MockKey('3')], name=name
    )
    return lambda *args, **kwargs: return_object


@pytest.fixture
def fuga_container(monkeypatch, connecting_s3):
    monkeypatch.setattr("fuga_object_store.boto.connect_s3", connecting_s3)
    fuga = FugaConnection("1", "2", "testing")
    return fuga


def test_context_manager_deletes_keys_with_container(monkeypatch,
                                                     connecting_s3):
    monkeypatch.setattr("fuga_object_store.boto.connect_s3", connecting_s3)

    with FugaConnection("1", "2", "") as fuga:
        assert fuga.connection is not None
        assert fuga.secret_key == "2"
        assert fuga.access_key == "1"

    assert fuga.connection is None
    assert fuga.secret_key is None
    assert fuga.access_key is None


def test_list_returns_correct_items(monkeypatch, connecting_s3):
    monkeypatch.setattr("fuga_object_store.boto.connect_s3", connecting_s3)
    with FugaConnection("1", "2", "test-container") as fuga:
        assert FugaContainer(fuga).list() == ['1', '2', '3']


def test_get_returns_correctly_hex(monkeypatch, connecting_s3):
    monkeypatch.setattr("fuga_object_store.boto.connect_s3", connecting_s3)
    with FugaConnection("1", "2", "test-container") as fuga:
        assert FugaContainer(fuga).get("3") == "AAAAAAAAAAAAAAAAAA=="


def test_get_returns_correctly_bin(monkeypatch, connecting_s3):
    monkeypatch.setattr("fuga_object_store.boto.connect_s3", connecting_s3)
    with FugaConnection("1", "2", "test-container") as fuga:
        assert FugaContainer(fuga).get("3", return_hex=False) == bytes(
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])


def test_contextmanager_is_the_same_as_object(monkeypatch, connecting_s3):
    monkeypatch.setattr("fuga_object_store.boto.connect_s3", connecting_s3)
    fuga1 = FugaConnection("1", "2", "test-container")
    with FugaConnection("1", "2", "test-container") as fuga2:
        assert dir(fuga1) == dir(fuga2)
        assert fuga1.access_key == fuga2.access_key
        assert fuga1.secret_key == fuga2.secret_key
        assert fuga1.connection.name == fuga2.connection.name


def test_connection_can_be_reset_correctly(monkeypatch, connecting_s3):
    monkeypatch.setattr("fuga_object_store.boto.connect_s3", connecting_s3)
    fuga = FugaConnection("1", "2", "test-container")
    assert '<FugaConnection: test-container>' == str(fuga)
    fuga.reset_connection('kaasmarkt')
    assert '<FugaConnection: kaasmarkt>' == str(fuga)


def test_delete_correctly(fuga_container):
    assert FugaContainer(fuga_container).delete('1') == "'1' deleted"


def test_upload_file_success(fuga_container):
    with BytesIO(b'hallo') as f:
        f.mode = 'rb'
        FugaContainer(fuga_container).upload(f, 'testing') == 'success'
        f.name = 'testing'
        FugaContainer(fuga_container).upload(f) == 'success'


def test_upload_file_fails_on_using_non_binairy_file(fuga_container):
    with BytesIO(b'hallo') as f:
        f.mode = 'r'
        with pytest.raises(IOError):
            FugaContainer(fuga_container).upload(f, 'testing')


def test_download_file_success(fuga_container):
    with BytesIO(b'') as f:
        f.mode = 'wb'
        FugaContainer(fuga_container).download(f, load_from='1') == 'success'
        f.name = '2'
        FugaContainer(fuga_container).download(f) == 'success'


def test_download_file_fails_on_using_binairy_file(fuga_container):
    with BytesIO(b'') as f:
        f.mode = 'w'
        with pytest.raises(IOError):
            FugaContainer(fuga_container).download(f, 'testing')


def test_get_file_fails_on_not_existing(fuga_container):
    with pytest.raises(AttributeError):
        FugaContainer(fuga_container).get('testing')


def test_container_init_fail_when_connection_attribute_is_none(fuga_container):
    fuga_container.connection = None
    with pytest.raises(ValueError):
        FugaContainer(fuga_container)


def test_container_init_fails_without_connection_attribute():
    with pytest.raises(AttributeError):
        FugaContainer("")


def test_object_store_works(monkeypatch, connecting_s3):
    monkeypatch.setattr("fuga_object_store.boto.connect_s3", connecting_s3)

    with FugaObjectStore("1", "2", "testing") as fuga:
        assert fuga.list() == ['1', '2', '3']
