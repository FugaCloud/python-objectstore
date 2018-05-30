
import boto
import boto.s3.connection
import base64
import os.path


class FugaContainer(object):
    """Class to interact with the Fuga Object Store."""

    def __init__(self, fuga_connection):
        try:
            if fuga_connection.connection is None:
                raise ValueError(
                    'Make sure that fuga_connection '
                    'is connected to a container')
        except AttributeError:
            raise AttributeError(
                'fuga_connection object has to have a connection attribute')

        self.fuga_connection = fuga_connection

    @property
    def _connection(self):
        return self.fuga_connection.connection

    def __repr__(self):
        return "<FugaContainer: {}>".format(self._connection.name)

    def list(self):
        """list everything in the container"""
        return [x.name for x in self._connection.list()]

    def get(self, filename, return_hex=True):
        """return the 'filename' from the container.
        If the return_hex flag is True (default)
        return the contents as hexadecimal binary,
        if the return_hex flag is False return standard python binary"""
        key = self._connection.get_key(filename)
        if key is None:
            raise AttributeError(
                'File {} not found in {}'.format(filename,
                                                 self.fuga_connection))
        bin_file = key.get_contents_as_string()
        if return_hex:
            bin_file = base64.b64encode(bin_file).decode("utf-8")
        return bin_file

    def delete(self, filename):
        """delete 'filename' from the container"""
        key = self._connection.get_key(filename)
        key.delete()
        return "'{}' deleted".format(filename)

    def upload(self, file, save_as=None):
        """upload the contents of local 'file' to 'basename(file.name)'
        or to 'save_as' in the container"""
        if 'b' not in file.mode:
            raise IOError('Use a binairy file to upload from')

        if save_as is None:
            name = os.path.basename(file.name)
        else:
            name = save_as
        key = self._connection.new_key(name)
        key.set_contents_from_file(file)
        return 'success'

    def download(self, file, load_from=None):
        """download the contents from the container with the name
        'basename(file.name)' or 'load_from' from the container
        to 'file' on the local computer"""
        if 'b' not in file.mode:
            raise IOError('Use a binairy file to download to')

        if load_from is None:
            file_from_container = self.get(
                os.path.basename(file.name), return_hex=False)
        else:
            file_from_container = self.get(load_from, return_hex=False)
        file.write(file_from_container)
        return 'success'


class FugaConnection(object):
    """Class to make a connection to the Fuga Object Store
     with a given container"""

    def __init__(self, access_key, secret_key, container_name):
        self.access_key = access_key
        self.secret_key = secret_key
        self.make_connection(container_name)

    def make_connection(self, container_name):
        """make connection to given container"""
        conn = boto.connect_s3(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            host='object.api.fuga.io',
            port=443,
            calling_format=boto.s3.connection.OrdinaryCallingFormat(),
        )
        self.connection = conn.get_bucket(container_name)

    def close_connection(self):
        """close connection to container"""
        self.connection.connection.close()
        self.connection = None

    def reset_connection(self, container_name):
        self.close_connection()
        self.make_connection(container_name)

    def __repr__(self):
        return "<FugaConnection: {}>".format(self.connection.name)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.access_key = None
        self.secret_key = None
        self.close_connection()


class FugaObjectStore(FugaContainer):
    """FugaObjectStore context manager. 
    Makes it easier to connect to the Fuga ObjectStore. 
    Example:

    with FugaObjectStore(ACCESS_KEY, SECRET_KEY, '<your-container-name>') as fuga:
        with open("local/path/where/file-to-upload-to-objectstore", 'rb') as f:
            fuga.upload(f)

        with open("local/path/where/file-to-download-from-objectstore", 'wb') as f:
            fuga.download(f, load_from='file-to-download-from-objectstore')
    """  # noqa

    def __init__(self, access_key, secret_key, container_name):
        cont = FugaConnection(access_key, secret_key,
                              container_name=container_name)
        self.fuga_container = FugaContainer(cont)
        self.fuga_connection = cont

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.fuga_connection.__exit__(*exc)
