Python Object to connect to the Fuga ObjectStore. With the basic CRUD methods. Use the static function 'FugaContainer.list_functions()' to get the available functions, or just read the python file.

To get started, download the file or copy paste it in your project and then:

```python
from object_store_object import FugaContainer

ACCESS_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
SECRET_KEY = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'

fuga = FugaContainer(ACCESS_KEY, SECRET_KEY)
fuga.set_container('<container-name>')
print(fuga)

print(FugaContainer.list_functions())
```

Now you will be able to upload a file to it with:

```python
fuga.upload_file("file/path/with/file-to-upload")
```

And get it back with:

```python
fuga.get_file("file-to-upload")
```

Or save it with (watch out it saves it relative to the pythonpath specified or where you saved this python script):
```python
fuga.save_file("file-from-object-store")
```

Run the tests with coverage report:

```bash
pytest --cov-report=html --cov
```
