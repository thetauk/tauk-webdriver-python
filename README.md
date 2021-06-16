# Tauk Python Package for WebDriver-based Tests
The Tauk Python Package allows you to easily report and monitor your Appium automation tests on the Tauk platform.

## Installation
```bash
$ pip install tauk
```

## Usage

### Import the Tauk package in your test suite. 

```python
from tauk import Tauk
```

### Initialize Tauk with your driver, `API TOKEN`, and `PROJECT ID`.
You can retrieve your `API TOKEN` and `PROJECT ID` from the Tauk Web UI. Your tokens can be generated and retrieved from the *User Settings > API Access* section. Each of your project cards will have their associated project id's in the *#* section.
```python
Tauk.initialize(api_token="API-TOKEN", project_id="PROJECT-ID", driver=self.driver)
```


If you want to exclude a test case from analysis you can pass in the argument `excluded=True`. For example:
```python
Tauk.initialize(api_token="API-TOKEN", project_id="PROJECT-ID", driver=self.driver, excluded=True)
```

### Decorate your individual test case methods with `@Tauk.observe`.
Add the `@Tauk.observe` decorator above the test case methods you want Tauk to watch.  For example:
```python
@Tauk.observe
def test_Contacts_AddNewContact(self):
	print("Clicking on the [Add] Button")
	self.wait.until(expected_conditions.presence_of_element_located(
		(MobileBy.ID, "com.android.contacts:id/floating_action_button"))
	).click()
```


### Call `Tauk.upload()` before ending your driver session.

```python
Tauk.upload()
```

### Recommendations for use in test frameworks
When using the Tauk package in test frameworks, such as `unittest` and `pytest`, here are some recommendations:
- Call `Tauk.initialize(...)` within the your set up method or fixture.
- Call `Tauk.upload()` in your teardown method or fixture.
