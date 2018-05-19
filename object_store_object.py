import base64
from os.path import basename

import boto
import boto.s3.connection
from boto.s3.key import Key


class FugaContainer(object):

    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.container = None

    def _fetch_container(self, container_name):
        if container_name is None:
            container = self.container
            if container is None:
                raise AttributeError('Container is not set')
        else:
            container = self.get_container(container_name)
        return container

    def get_container(self, container_name):
        return self.set_container(container_name, set_object=False)

    def set_container(self, container_name, set_object=True):
        conn = boto.connect_s3(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            host='object.api.fuga.io',
            port=443,
            calling_format=boto.s3.connection.OrdinaryCallingFormat(),
        )
        container = conn.get_bucket(container_name)
        if set_object:
            self.container = container
        return container


    def upload_file(self, file, container_name=None):
        container = self._fetch_container(container_name)
        with open(file, 'rb') as f:
            name = basename(f.name)
            k = container.new_key(name)
            k.set_contents_from_file(f)

    def get_files(self, container_name=None, return_binary=False, limit=None):
        files = {}
        container = self._fetch_container(container_name)

        for i, key in enumerate(container.list()):
            file = key.get_contents_as_string()
            if not return_binary:
                file = base64.b64encode(file).decode("utf-8")
            files.update({key.name: file})

            if limit is not None:
                if i == limit-1:
                    break
        return files

    def get_file(self, filename, container_name=None, return_binary=False):
        container = self._fetch_container(container_name)
        if filename in [x.name for x in container.list()]:
            key = container.get_key(filename)
            file = key.get_contents_as_string()
            if not return_binary:
                file = base64.b64encode(file).decode("utf-8")
            return file
        raise AttributeError('File not found')

    def post_file(self, file, container_name=None):
        """file is the file returned by the flask method 'request.files' of type 'werkzeug.datastructures.FileStorage'"""
        container = self._fetch_container(container_name)
        name = file.filename
        if name == "":
            raise AttributeError('File not found')
        k = container.new_key(name)
        k.set_contents_from_file(file)
        return 'success'

    def delete_file(self, filename, container_name=None):
        container = self._fetch_container(container_name)
        if filename in [x.name for x in container.list()]:
            k = container.get_key(filename)
            k.delete()
            return "'{}' deleted".format(filename)

        raise AttributeError('File not found')

    def save_file(self, filename, container_name=None):
        """saves the 'filename' from the container to 'filename' on the local computer"""
        container = self._fetch_container(container_name)
        file = self.get_file(filename, container, return_binary=True)
        with open(filename, 'wb') as f:
            f.write(file)

        return 'successfully saved file'

    def list_files(self, container_name=None):
        container = self._fetch_container(container_name)
        return [x.name for x in container.list()]

    def __repr__(self):
        base_repr = "FugaContainer(access_key={}, secret_key=<secret_key>)".format(
            self.access_key)
        if self.container is None:
            return base_repr
        return "{} with container {}".format(base_repr, self.container)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.access_key = None
        self.secret_key = None
        self.container.connection.close()
        self.container = None
        return True

    @staticmethod
    def list_functions():
        return [x for x in dir(FugaContainer) if not x.startswith("_")]
