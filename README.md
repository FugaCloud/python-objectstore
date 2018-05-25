# Connecting to Fuga ObjectStore with Python

A collection of Python Objects to connect to the Fuga ObjectStore. It is a small wrapper around boto. 

To get started, download the file or copy paste it in your project, install the requirements.txt and then:

```python
from fuga_object_store import FugaObjectStore

ACCESS_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
SECRET_KEY = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'

with FugaObjectStore(ACCESS_KEY, SECRET_KEY, '<your-container-name>') as fuga:
    print(fuga.list())

```

This will list all the files in your container. You will now be able to get en delete files from your Container with:

```python
with FugaObjectStore(ACCESS_KEY, SECRET_KEY, '<your-container-name>') as fuga:
    print(fuga.get('filename'))
    # or
    print(fuga.delete('filename'))
```

The 'get' method will return the binary contents of the file and encode it as hexadecimal number, this can be embedded in a html page. With the return_hex flag to False this method will return raw bytes.
There are methods for uploading and downloading files. These will need a file-like object to save or load from. For example:

```python
with FugaObjectStore(ACCESS_KEY, SECRET_KEY, '<your-container-name>') as fuga:
    with open("local/path/where/file-to-upload-to-objectstore", 'rb') as f:
        fuga.upload(f)

    with open("local/path/where/file-to-download-from-objectstore", 'wb') as f:
        fuga.download(f, load_from='file-to-download-from-objectstore')
```

FugaObjectStore class is a combination of the FugaInterface class and the FugaContainer class. The FugaInterface takes a FugaContainer-like object as its input and makes it possible to use its interface.

```python
with FugaContainer(ACCESS_KEY, SECRET_KEY, '<your-container-name>') as fuga:
    print(FugaInterface(fuga).list())

```

You will also be able to use these classes without context manager this way:

```python
container = FugaContainer(ACCESS_KEY, SECRET_KEY)
container.make_connection('<your-container-name>')

interface = FugaInterface(container)
print(interface.list())  # Or upload and download files

container.close_connection()

```

Run the tests with:

```bash
PYTHONPATH=. pytest
```
