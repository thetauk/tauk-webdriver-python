# Tauk Python Package for WebDriver-based Tests
The Tauk Python Package allows you to easily report and monitor your Appium and Selenium automation tests on the 
Tauk platform.

## Installation
```bash
$ pip install tauk
```

## Usage

### Import the Tauk package in your test suite. 

```python
from tauk.tauk_webdriver import Tauk
```

### Initialize Tauk with your driver, `API TOKEN`, and `PROJECT ID`.
You only have to initialize Tauk() once for the entire execution. 
You can retrieve your `API TOKEN` and `PROJECT ID` from the Tauk Web UI. 
Your tokens can be generated and retrieved from the *User Settings > API Access* section. 
Each of your project cards will have their associated project id's in the *#* section.
```python
Tauk(api_token="API-TOKEN", project_id="PROJECT-ID")
```

Additionally, if you are running tests in parallel and each test runs in a different process you should include the 
`multi_process_run=True` flag when initializing tauk so that it can tie multiple processes with the same execution.
```python
Tauk(api_token="API-TOKEN", project_id="PROJECT-ID", multi_process_run=True)
```


### Decorate your individual test case methods with `@Tauk.observe`.
Add the `@Tauk.observe` decorator above the test case methods you want Tauk to watch.  For example:
```python
@Tauk.observe(custom_test_name='Add New Contact', excluded=False)
def test_Contacts_AddNewContact(self):
	print("Clicking on the [Add] Button")
	self.wait.until(expected_conditions.presence_of_element_located(
		(MobileBy.ID, "com.android.contacts:id/floating_action_button"))
	).click()
```

If you want to exclude a test case from analysis you can pass in the argument `excluded=True`. For example:
```python
@Tauk.observe(custom_test_name='Add New Contact', excluded=True)
```

For webdriver based tests Tauk can collect useful information list screenshot, view hierarchy etc. from the application. 
In order to support that you can simply register the driver instance at the beginning of the test using 
`Tauk.register_driver()`.
```python
def test_Contacts_AddNewContact(self):
	print("Clicking on the [Add] Button")
	Tauk.register_driver(self.driver)
	self.wait.until(expected_conditions.presence_of_element_located(
		(MobileBy.ID, "com.android.contacts:id/floating_action_button"))
	).click()
```

*For sample code, please take a look at the `android_contacts_tests.py` test case in the `tests` directory of the repository.*

### Tauk Listeners

If you are using [unittest](https://docs.python.org/3/library/unittest.html) for test automation, Tauk comes packaged with a test listener which can hook onto the test lifecycle and extract test information.
When using a test listener you no longer have to decorate the test method with `Tauk.observe()`

You can use Tauk listener as follows
```python
from tauk.listeners.unittest_listener import TaukListener

if __name__ == '__main__':
    ...
    suite = unittest.TestSuite()
    suite.addTest(AndroidContactsTest('test_Contacts_AddNewContact'))
    unittest.TextTestRunner(resultclass=TaukListener).run(suite)
    ...
```

