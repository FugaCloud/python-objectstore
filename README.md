Python Object to connect to the Fuga ObjectStore. With the basic CRUD methods. Use the static function 'FugaContainer.list_functions()' to get the available functions, or just read the python file.

To get started:

ACCESS_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
SECRET_KEY = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'

fuga = FugaContainer(ACCESS_KEY, SECRET_KEY)
fuga.set_container('<container-name>')
print(fuga)

print(FugaContainer.list_functions())

Now you will be able to upload a file to it with:

fuga.upload_file("file/path/with/file")

And get it back with:

fuga.get_file("file")

Or save it with (watch out it saves it relative to the pythonpath specified or where you saved this python script):

fuga.save_file("file")


Run the tests with coverage report:
pytest --cov-report=html --cov
