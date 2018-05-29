import pytest
from unittest.mock import Mock
from fuga_object_store import FugaContainer, FugaInterface, FugaObjectStore
from io import BytesIO


class MockConnectionReturnValue(object):

    def __init__(self, listvalue):
        self.name = 'test'
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
    mock_connection = MockConnectionReturnValue(
        listvalue=[MockKey('1'), MockKey('2'), MockKey('3')]
    )
    return Mock(get_bucket=lambda x: mock_connection)


@pytest.fixture
def fuga_container(monkeypatch, connecting_s3):
    monkeypatch.setattr("fuga_object_store.boto.connect_s3", connecting_s3)
    fuga = FugaContainer("1", "2", "testing")
    fuga.connection = connecting_s3.get_bucket("")
    return fuga


def test_connection_is_none_when_not_given():
    fuga = FugaContainer("", "")
    assert fuga.connection is None

    with pytest.raises(AttributeError):
        fuga.close_connection()


def test_context_manager_deletes_keys_without_container():
    with FugaContainer("1", "2") as fuga:
        assert fuga.connection is None
        assert fuga.secret_key == "2"
        assert fuga.access_key == "1"

    assert fuga.connection is None
    assert fuga.secret_key is None
    assert fuga.access_key is None


def test_context_manager_deletes_keys_with_container(monkeypatch,
                                                     connecting_s3):
    monkeypatch.setattr("fuga_object_store.boto.connect_s3", connecting_s3)

    with FugaContainer("1", "2", "") as fuga:
        assert fuga.connection is not None
        assert fuga.secret_key == "2"
        assert fuga.access_key == "1"

    assert fuga.connection is None
    assert fuga.secret_key is None
    assert fuga.access_key is None


def test_list_returns_correct_items(monkeypatch, connecting_s3):
    monkeypatch.setattr("fuga_object_store.boto.connect_s3", connecting_s3)
    with FugaContainer("1", "2", "test-container") as fuga:
        fuga.connection = connecting_s3.get_bucket("")
        assert FugaInterface(fuga).list() == ['1', '2', '3']


def test_get_returns_correctly_hex(monkeypatch, connecting_s3):
    monkeypatch.setattr("fuga_object_store.boto.connect_s3", connecting_s3)
    with FugaContainer("1", "2", "test-container") as fuga:
        fuga.connection = connecting_s3.get_bucket("")
        assert FugaInterface(fuga).get("3") == "AAAAAAAAAAAAAAAAAA=="


def test_get_returns_correctly_bin(monkeypatch, connecting_s3):
    monkeypatch.setattr("fuga_object_store.boto.connect_s3", connecting_s3)
    with FugaContainer("1", "2", "test-container") as fuga:
        fuga.connection = connecting_s3.get_bucket("")
        assert FugaInterface(fuga).get("3", return_hex=False) == bytes(
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])


def test_contextmanager_is_the_same_as_object(monkeypatch, connecting_s3):
    monkeypatch.setattr("fuga_object_store.boto.connect_s3", connecting_s3)
    fuga1 = FugaContainer("1", "2", "test-container")
    fuga1.connection = connecting_s3.get_bucket("")
    with FugaContainer("1", "2", "test-container") as fuga2:
        fuga2.connection = connecting_s3.get_bucket("")
        assert dir(fuga1) == dir(fuga2)
        assert fuga1.__dict__ == fuga2.__dict__


def test_delete_correctly(fuga_container):
    assert FugaInterface(fuga_container).delete('1') == "'1' deleted"


def test_upload_file_success(fuga_container):
    with BytesIO(b'hallo') as f:
        f.mode = 'rb'
        FugaInterface(fuga_container).upload(f, 'testing') == 'success'
        f.name = 'testing'
        FugaInterface(fuga_container).upload(f) == 'success'


def test_upload_file_fails_on_using_non_binairy_file(fuga_container):
    with BytesIO(b'hallo') as f:
        f.mode = 'r'
        with pytest.raises(IOError):
            FugaInterface(fuga_container).upload(f, 'testing')


def test_download_file_success(fuga_container):
    with BytesIO(b'') as f:
        f.mode = 'wb'
        FugaInterface(fuga_container).download(f, load_from='1') == 'success'
        f.name = '2'
        FugaInterface(fuga_container).download(f) == 'success'


def test_download_file_fails_on_using_binairy_file(fuga_container):
    with BytesIO(b'') as f:
        f.mode = 'w'
        with pytest.raises(IOError):
            FugaInterface(fuga_container).download(f, 'testing')


def test_get_file_fails_on_not_existing(fuga_container):
    with pytest.raises(AttributeError):
        FugaInterface(fuga_container).get('testing')


def test_interface_init_fail_when_connection_attribute_is_none(fuga_container):
    fuga_container.connection = None
    with pytest.raises(ValueError):
        FugaInterface(fuga_container)


def test_interface_init_fails_without_connection_attribute():
    with pytest.raises(AttributeError):
        FugaInterface("")


def test_object_store_works(monkeypatch, connecting_s3):
    monkeypatch.setattr("fuga_object_store.boto.connect_s3", connecting_s3)

    with FugaObjectStore("1", "2", "testing") as fuga:
        fuga.fuga_container.connection = connecting_s3.get_bucket("")
        assert fuga.list() == ['1', '2', '3']


def test_repr_working_for_fuga_container_without_container(monkeypatch,
                                                           connecting_s3):
    monkeypatch.setattr("fuga_object_store.boto.connect_s3", connecting_s3)
    with FugaContainer("1", "2") as fuga:
        assert str(fuga) == '<FugaContainer>'
