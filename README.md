<!-- TOC -->
  * [1. Using assert Statements](#1-using-assert-statements)
  * [Pytest](#pytest)
  * [**How to run tests?**](#how-to-run-tests)
    * [Run tests in a module](#run-tests-in-a-module)
    * [Run tests in a directory](#run-tests-in-a-directory)
    * [Run tests by keyword expressions](#run-tests-by-keyword-expressions)
    * [What is Mock?](#what-is-mock)
      * [When to use Mock?](#when-to-use-mock)
    * [What is decorator?](#what-is-decorator)
    * [What is marks?](#what-is-marks)
      * [Marking tests with custom markers](#marking-tests-with-custom-markers)
    * [What are fixtures?](#what-are-fixtures)
      * [Use case:](#use-case)
<!-- TOC -->

## 1. Using assert Statements

Use assert during development to:

* Check conditions you believe will always hold (invariants).
* Validate logic and assumptions.
* Simplify debugging and testing.
* Avoid assert in production code where critical validations and user-facing checks are needed, as assert statements
  might be ignored when optimization flags are used.

```pyhton
def my_power(base, exponent):
    result = 1
    for i in range(exponent):
        result = result * 5

    return result

def test_scenario_1():
    assert my_power(6, 3) == pow(base=6, exp=3), "Incorrect result from my_power() function"
```

## Pytest

**Step 1:**

Installation:
`pip install pytest`

**Step 2:**

in the terminal we write: `pytest`, please make sure you have `*.py` files with the prefix: `test_`,
this way pytest will know what files to run.
the functions in the file should with the word `test`.
pytest will run all files of the form test_*.py or *_test.py in the current directory and its subdirectories.

**Group multiple tests in a class**
Grouping tests in classes can be beneficial for the following reasons:

* Test organization

* Sharing fixtures for tests only in that particular class

* Applying marks at the class level and having them implicitly apply to all tests

There is no need to subclass anything, **but make sure to prefix your class with Test otherwise the class will be
skipped**. We can simply run the module by passing its filename

```bashREADME.md
pytest -q test_class.py
```

```python
class TestClassDemoInstance:
    value = 0

    def test_one(self):
        self.value = 1
        assert self.value == 1

    def test_two(self):
        assert self.value == 1
```

## **How to run tests?**

### Run tests in a module

```shell
pytest test_mod.py
```

### Run tests in a directory

```shell
pytest testing/
```

### Run tests by keyword expressions

```shell
pytest -k 'power'
```

For example:

```python
def my_power(base, exponent):
    result = 1
    for i in range(exponent):
        result = result * 5

    return result


def my_factorial(number):
    result = 1
    for i in range(1, number + 1):
        result = result * 5

    return result


def test_scenario_power_1():
    assert my_power(6, 3) == pow(base=6, exp=3), "Incorrect result from my_power() function"
    print('King Mory')


def test_scenario_2():
    assert my_factorial(5) == 125, "Incorrect result from my_power() function"
    print('King Mory')
```

I would like to run only tests with the keyword `power`,
therefore I'll write `pytest -k power`

### What is Mock?

in Python is used to create mock objects, which simulate the behavior of real objects in tests without requiring the
actual objects or resources. This helps isolate the code being tested and makes tests faster and more reliable

#### When to use Mock?

The use cases:

1) When your code interacts with external APIs (Remote service)
2) When your code interacts with filesystem
3) If you need to test a function that uses objects with complex dependencies.
4) When you want to test a component in **isolation without involving other parts of the system**.
5) For simulating edge cases like **network failures or specific error responses**.

Example for usecase:

Invoking api (external service):

```python
def get_user_data(user_id):
    response = requests.get(f"https://jsonplaceholder.typicode.com/users/{user_id}")
    if response.status_code == 200:
        return response.json()
    return None
```

Here is the test, I'm using mock:

```python
def test_get_user_data():
    # Create a mock response object
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"name": "John Doe", "age": 30}

    # Mock the requests.get call
    requests.get = Mock(return_value=mock_response)

    # Call the function under test
    result = get_user_data(10)

    # Assertions to verify behavior
    assert result == {"name": "John Doe", "age": 30}
    requests.get.assert_called_once_with("https://jsonplaceholder.typicode.com/users/10")
```

### What is decorator?

A decorator in Python is a design pattern that allows you to extend or modify the behavior of a function or method
without permanently modifying its structure.

### What is marks?

marks are used to categorize and selectively run tests. Marks help in organizing test cases based on criteria like
functionality, speed, or priority.

#### Marking tests with custom markers

```python
@pytest.mark.slow
def test_slow_operation():
    import time
    time.sleep(2)
    assert True


@pytest.mark.fast
def test_fast_operation():
    assert 1 + 1 == 2


@pytest.mark.database
def test_database_query():
    assert "data" in ["data", "test", "info"]
```

In case we would like to run only the slow category we will write:

```bash
pytest -m slow
```

In case we would like to run either `slow` or `database` category we will write,
to run multiple markers:

```bash
pytest -m "slow or database"
```

### What are fixtures?

A fixture in pytest is a **reusable piece of code** used to **set up a consistent test environment before running tests
** and can also **help clean up after tests**. Fixtures are commonly used for tasks like **database setup**, **creating
test data**,
**initializing web drivers**, or **preparing mock objects**.

#### Use case:

Here we have 2 simple routes (`/add_movie`, `/get_movies`):

```python
# app.py
from flask import Flask, request, jsonify

app = Flask(__name__)
movies = []


@app.route('/add_movie', methods=['POST'])
def add_movie():
    movie = request.json.get('title')
    if movie:
        movies.append(movie)
        return jsonify({"message": "Movie added successfully!"}), 201
    return jsonify({"error": "No movie provided"}), 400


@app.route('/get_movies', methods=['GET'])
def get_movies():
    return jsonify({"movies": movies}), 200

```

Here we write the fixture (a reusable piece of code used to set up a consistent test environment
before running tests and can also help clean up after tests)

```python
# conftest.py
import pytest
from app import app, movies


@pytest.fixture
def test_client():
    """Fixture to create a test client and ensure a clean state."""
    app.testing = True
    client = app.test_client()
    movies.clear()  # Clear movie list before each test
    yield client
```

We can easily see for each tests (3 tests), we call the fixture function (`test_client`).

```python
# test_flask_app.py
def test_add_movie(test_client):
    """Test adding a valid movie."""
    response = test_client.post('/add_movie', json={"title": "Inception"})
    assert response.status_code == 201
    assert b"Movie added successfully!" in response.data
    assert "Inception" in movies


def test_add_movie_no_title(test_client):
    """Test adding a movie without a title."""
    response = test_client.post('/add_movie', json={})
    assert response.status_code == 400
    assert b"No movie provided" in response.data


def test_get_movies(test_client):
    """Test retrieving movies."""
    test_client.post('/add_movie', json={"title": "Inception"})
    response = test_client.get('/get_movies')
    assert response.status_code == 200
    assert b"Inception" in response.data
```

This setup ensures a clean database for every test run.