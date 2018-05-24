from object_store_object import FugaContainer
import pytest
from unittest.mock import patch, Mock, mock_open
from boto.exception import S3ResponseError


class MockConnectionReturnValue(object):

    def __init__(self, listvalue):
        self.listvalue = listvalue
        self.connection = MockFile("")

    def list(self):
        return self.listvalue

    def get_key(self, *args, **kwargs):
        return MockFile(args[0])

    def new_key(self, *args, **kwargs):
        return MockFile(args[0])


class MockFile(object):

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


@pytest.mark.skip
def test_forbidden_not_access_keys(mock_boto):
    with pytest.raises(S3ResponseError):
        FugaContainer("", "").set_container("test")


@pytest.fixture
def connecting_s3():
    mock_connection = MockConnectionReturnValue(
        listvalue=[MockFile('1'), MockFile('2'), MockFile('3')])
    mock_connect = Mock()
    mock_connect.get_bucket.side_effect = lambda x: mock_connection
    return mock_connect


@patch('object_store_object.boto')
def test_set_container_sets_container(mock_boto):
    mock_connect = Mock()
    mock_connect.get_bucket.side_effect = lambda x: 'testing'
    mock_boto.connect_s3.return_value = mock_connect
    fuga = FugaContainer("", "")
    fuga.set_container("testing")
    assert fuga.container == 'testing'


@patch('object_store_object.boto')
def test_get_container_does_not_set_container(mock_boto):
    mock_connect = Mock()
    mock_connect.get_bucket.side_effect = lambda x: 'testing'
    mock_boto.connect_s3.return_value = mock_connect
    fuga = FugaContainer("", "")
    fuga.get_container("testing")
    assert fuga.container != 'testing'


def test_getfile_none_container_raises_error():
    fuga = FugaContainer("", "")

    with pytest.raises(AttributeError):
        fuga.get_file("")


def test_getfiles_none_container_raises_error():
    fuga = FugaContainer("", "")

    with pytest.raises(AttributeError):
        fuga.get_files()


def test_delete_file_none_container_raises_error():
    fuga = FugaContainer("", "")

    with pytest.raises(AttributeError):
        fuga.delete_file("")


def test_save_file_none_container_raises_error():
    fuga = FugaContainer("", "")

    with pytest.raises(AttributeError):
        fuga.save_file("")


def test_upload_file_none_container_raises_error():
    fuga = FugaContainer("", "")

    with pytest.raises(AttributeError):
        fuga.upload_file("")


def test_list_files_none_container_raises_error():
    fuga = FugaContainer("", "")

    with pytest.raises(AttributeError):
        fuga.list_files()


def test_list_all_the_functions():

    assert set(FugaContainer.list_functions()) == {
        'delete_file', 'get_container',
        'get_file', 'get_files',
        'list_functions', 'post_file',
        'save_file', 'set_container',
        'upload_file', 'list_files'
    }


@patch('object_store_object.boto')
def test_fuga_container_repr_function(mock_boto, connecting_s3):
    fuga = FugaContainer("", "")
    assert str(fuga) == "FugaContainer(access_key="", secret_key=<secret_key>)"

    mock_connect = Mock()
    mock_connect.get_bucket.side_effect = lambda x: 'test'
    mock_boto.connect_s3.return_value = mock_connect

    fuga.set_container("test")
    assert str(fuga) == ("FugaContainer(access_key=, "
                         "secret_key=<secret_key>) with container test")


@patch('object_store_object.boto')
def test_list_files_function(mock_boto, connecting_s3):
    fuga = FugaContainer("", "")

    mock_boto.connect_s3.return_value = connecting_s3

    assert fuga.list_files("") == ['1', '2', '3']
    fuga.set_container("")
    assert fuga.list_files() == ['1', '2', '3']


@patch('object_store_object.boto')
def test_delete_file_succeeds(mock_boto, connecting_s3):
    fuga = FugaContainer("", "")

    mock_boto.connect_s3.return_value = connecting_s3
    assert fuga.delete_file("1", "") == "'1' deleted"
    fuga.set_container("")
    assert fuga.delete_file("2") == "'2' deleted"


@patch('object_store_object.boto')
def test_delete_file_fails(mock_boto, connecting_s3):
    fuga = FugaContainer("", "")

    mock_boto.connect_s3.return_value = connecting_s3
    with pytest.raises(AttributeError):
        fuga.delete_file("4", "")
    fuga.set_container("")
    with pytest.raises(AttributeError):
        fuga.delete_file("4")


@patch('object_store_object.boto')
def test_save_file_succeeds(mock_boto, connecting_s3):
    fuga = FugaContainer("", "")

    mock_boto.connect_s3.return_value = connecting_s3
    fuga.set_container("")

    with patch("builtins.open", mock_open()):
        fuga.save_file("1")


@patch('object_store_object.boto')
def test_get_file(mock_boto, connecting_s3):
    fuga = FugaContainer("", "")

    mock_boto.connect_s3.return_value = connecting_s3
    fuga.set_container("")

    with patch("builtins.open", mock_open()):
        fuga.get_file("1")


@patch('object_store_object.boto')
def test_get_file_doesnt_exist(mock_boto, connecting_s3):
    fuga = FugaContainer("", "")

    mock_boto.connect_s3.return_value = connecting_s3
    fuga.set_container("")

    with pytest.raises(AttributeError):
        fuga.get_file("4")


@patch('object_store_object.boto')
@patch('object_store_object.basename')
def test_upload_file_works(mock_basename, mock_boto, connecting_s3):
    fuga = FugaContainer("", "")

    mock_boto.connect_s3.return_value = connecting_s3
    fuga.set_container("")

    with patch("builtins.open", mock_open()):
        fuga.upload_file("4")


@patch('object_store_object.boto')
def test_get_files_no_limit(mock_boto, connecting_s3):
    fuga = FugaContainer("", "")

    mock_boto.connect_s3.return_value = connecting_s3
    fuga.set_container("")

    fuga.get_files()


@patch('object_store_object.boto')
def test_get_files_with_limit(mock_boto, connecting_s3):
    fuga = FugaContainer("", "")

    mock_boto.connect_s3.return_value = connecting_s3
    fuga.set_container("")

    assert len(fuga.get_files(limit=2)) == 2


@patch('object_store_object.boto')
def test_post_file(mock_boto, connecting_s3):
    fuga = FugaContainer("", "")

    mock_boto.connect_s3.return_value = connecting_s3
    fuga.set_container("")

    new_file = MockFile('testintest')
    assert fuga.post_file(new_file) == 'success'


@patch('object_store_object.boto')
def test_post_file_without_name_raises_attribute_error(mock_boto,
                                                       connecting_s3):
    fuga = FugaContainer("", "")

    mock_boto.connect_s3.return_value = connecting_s3
    fuga.set_container("")

    new_file = MockFile('')
    with pytest.raises(AttributeError):
        fuga.post_file(new_file)


@patch('object_store_object.boto')
def test_contextmanager_connection(mock_boto, connecting_s3):
    fuga = FugaContainer("", "")

    mock_boto.connect_s3.return_value = connecting_s3
    with FugaContainer("", "") as fuga:
        fuga.set_container("testing")

    assert fuga.container is None
    assert fuga.secret_key is None
    assert fuga.access_key is None
