
import boto
import boto.s3.connection
import base64
import os.path
ACCESS_KEY = '29aba3ce5c70426084844bc10e2dd86b'
SECRET_KEY = 'b6274b5c96cc40639151ada6bac03833'


class FugaObjectStore(object):
    """Class to interact with the Fuga Object Store."""
    def __init__(self, fuga_container):
        try:
            if fuga_container.connection is None:
                raise ValueError(
                    'Make sure that fuga_container is connected to a container')
        except AttributeError:
            raise AttributeError(
                'fuga_container object has to have a connection attribute')

        self.fuga_container = fuga_container

    @property
    def _connection(self):
        return self.fuga_container.connection

    def list(self):
        """list everything in the container"""
        return [x.name for x in self._connection.list()]

    def get(self, filename, return_hex=True):
        """return the 'filename' from the container.
        If the return_hex flag is True (default) return the contents as hexadecimal binairy, 
        if the return_hex flag is False return standard python binairy"""
        key = self._connection.get_key(filename)
        if key is None:
            raise AttributeError(
                'File {} not found in {}'.format(filename, self.fuga_container))
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
        """upload the contents of local 'file' to 'basename(file.name)' or to 'save_as' in the container"""
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
        """download the contents from the container with the name 'basename(file.name)' or 'load_from' from the container to 'file' on the local computer"""
        if 'b' not in file.mode:
            raise IOError('Use a binairy file to download to')

        if load_from is None:
            file_from_container = self.get(
                os.path.basename(file.name), return_hex=False)
        else:
            file_from_container = self.get(load_from, return_hex=False)
        file.write(file_from_container)
        return 'success'


class FugaContainer(object):
    """Class to make a connection to the Fuga Object Store with a given container"""
    def __init__(self, access_key, secret_key, container_name=None):
        self.access_key = access_key
        self.secret_key = secret_key
        if container_name is None:
            self.connection = None
        else:
            self.make_connection(container_name)

    def make_connection(self, container_name):
        conn = boto.connect_s3(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            host='object.api.fuga.io',
            port=443,
            calling_format=boto.s3.connection.OrdinaryCallingFormat(),
        )
        self.connection = conn.get_bucket(container_name)

    def close_connection(self):
        self.connection.connection.close()
        self.connection = None

    def __repr__(self):
        if self.connection:
            return "<FugaContainer: {}>".format(self.connection.name)
        else:
            return "<FugaContainer>"

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.access_key = None
        self.secret_key = None
        if self.connection is not None:
            self.close_connection()
        return True


if __name__ == "__main__":
    # with FugaContainer(ACCESS_KEY, SECRET_KEY) as fuga:
    #     fuga.make_connection('flask-test-wauw')
    #     print(FugaInteract(fuga).list_files())

    container = FugaContainer(ACCESS_KEY, SECRET_KEY, 'flask-test-wauw')
    fuga = FugaObjectStore(container)
    print(fuga.list())
    # print(fuga.get('cysologo.png'))

    with open("/home/thomas/Overig/TEAM A - Scrum statistieken.xlsx", "rb") as file:
        pass
        # fuga.upload(file, "kaas/baas.txt")
        # fuga.upload(file, "harry.xlsx")
    with open("/home/thomas/Videos/Blue_Particle_Motion_Background_1080.mov", "wb") as file:
        # fuga.download(file)
        pass
