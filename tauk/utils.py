import logging
import re
import requests

logger = logging.getLogger('tauk')


def get_appium_server_version(driver):
    driver_url = driver.command_executor._url
    response = requests.get(f'{driver_url}/status')
    if response.status_code == 200:
        try:
            json_response = response.json()
            return json_response['value']['build']['version']
        except KeyError:
            pass
    return None


def get_browser_driver_version(driver):
    browser_name = driver.capabilities.get('browserName', '')
    if browser_name == 'chrome':
        return driver.capabilities['chrome']['chromedriverVersion']
    elif browser_name == 'firefox':
        return driver.capabilities['moz:geckodriverVersion']
    elif browser_name == 'msedge':
        return driver.capabilities['msedge']['msedgedriverVersion']
    else:
        return None


def shortened_json(json_text):
    json_text = re.sub(r'"screenshot": ".+?"', '"screenshot" : "stripped"', json_text, flags=re.DOTALL)
    json_text = re.sub(r'"view": ".+?", ', '"view" : "stripped", ', json_text, flags=re.DOTALL)
    json_text = re.sub(r'"log": \[.+?}\], "', '"log": ["stripped"], "', json_text, flags=re.DOTALL)
    return json_text
