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

 There is no need to subclass anything, **but make sure to prefix your class with Test otherwise the class will be skipped**. We can simply run the module by passing its filename

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


### What is decorator?

### How to use fixtures?


