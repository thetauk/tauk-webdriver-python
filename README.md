# Tauk Python Package for WebDriver-based Tests

The Tauk Python Package allows you to easily report and monitor your Appium and Selenium automation tests on the Tauk platform.

## Installation

```bash
$ pip install tauk
```



## Usage

### Import the Tauk and TaukConfig classes from the package in your test suite.

```python
from tauk.tauk_webdriver import Tauk
from tauk.config import TaukConfig
```



### Initialize Tauk with your driver, `API TOKEN`, and `PROJECT ID`.

You only have to initialize the Tauk class once for the entire execution. 
You can retrieve your `API TOKEN` and `PROJECT ID` from the Tauk Web UI. 
Your tokens can be generated and retrieved from the _User Settings > API Access_ section. 
Each of your project cards will have their associated Project ID's in the _#_ section.

```python
Tauk(TaukConfig(api_token="API-TOKEN", project_id="PROJECT-ID"))
```

Additionally, if you are running tests in parallel and each test runs in a different process, 
you should include the `multi_process_run=True` flag when initializing Tauk 
so that it can tie multiple processes with the same execution.

```python
Tauk(TaukConfig(api_token="API-TOKEN", project_id="PROJECT-ID", multiprocess_run=True))
```

Alternatively, you can also pass these argument inputs through environment variables instead of through the `TaukConfig` class. 
In your local environment, you can set the following variables:

```bash
TAUK_API_TOKEN=YOUR-API-TOKEN
TAUK_PROJECT_ID=YOUR-PROJECT-ID

# If you have a multiprocess run
TAUK_MULTI_PROCESS=true

# Useful if you running multiple instances of you project. 
# Tauk will automatically use the process ID to create the execution context, 
# but you can override this behavior and provide an explicit execution dir if needed
TAUK_EXEC_DIR=/tmp/tauk/smoke_runs
```

If you're passing these inputs through environment variables, 
you conveniently don't need to explicitly initialize the Tauk class in your code. 
Instead, the Tauk class will check your environment variables on invocation. 
In other words, if you have the inputs as environment variables you can just import Tauk.



### Decorate your individual test case methods with `@Tauk.observe`.

Add the `@Tauk.observe` decorator above the test case methods you want Tauk to watch. For example:

```python
@Tauk.observe(custom_test_name='Add New Contact', excluded=False)
def test_Contacts_AddNewContact(self):
	print("Clicking on the [Add] Button")
	self.wait.until(expected_conditions.presence_of_element_located(
		(MobileBy.ID, "com.android.contacts:id/floating_action_button"))
	).click()
```

For WebDriver based tests Tauk can collect useful information such as the screenshot, 
view hierarchy, etc. from the application. In order to support that you can simply register the driver instance 
at the beginning of the test using `Tauk.register_driver()`.

```python
def test_Contacts_AddNewContact(self):
	print("Clicking on the [Add] Button")
	Tauk.register_driver(self.driver)
	self.wait.until(expected_conditions.presence_of_element_located(
		(MobileBy.ID, "com.android.contacts:id/floating_action_button"))
	).click()
```

Alternatively if the driver object is constructed in a base class (Ex: in the `setUp()` method), 
you also have to pass the `self` object as `unittestcase` argument. 
This will allow Tauk to collect details about the test.

```python
    def setUp(self) -> None:
        self.driver = webdriver.Chrome()
        Tauk.register_driver(self.driver, unittestcase=self)
```

_For sample code, please take a look at the `e2e/custom_integration_test.py` test case in the `tests` directory of the repository._



### Tauk Listeners

If you are using [unittest](https://docs.python.org/3/library/unittest.html) for structuring your tests, Tauk comes packaged with a test listener which can hook onto the test lifecycle and extract test information. When using a test listener you no longer have to decorate the test method with `Tauk.observe()`

You can use Tauk listener as follows:

```python
import unittest
from tauk.listeners.unittest_listener import TaukListener

if __name__ == '__main__':
    ...
    suite = unittest.TestSuite()
    suite.addTest(AndroidContactsTest('test_Contacts_AddNewContact'))
    unittest.TextTestRunner(resultclass=TaukListener).run(suite)
    ...
```

### Excluding tests

If you want to exclude a test case from analysis you can pass in as an argument `excluded=True` to `observe()` method. For example:

```python
@Tauk.observe(custom_test_name='Add New Contact', excluded=True)
```

For tests written using unittest framework you can skip tauk reporting by setting an instance variable
either in the base class that extends `unittest.TestCase` or directly in the testcase that extends `unittest.TestCase`

```python
import unittest


class TestDataTest(unittest.TestCase):
    tauk_skip = True

    ...

```