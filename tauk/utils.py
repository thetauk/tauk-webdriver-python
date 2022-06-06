import logging
import os
import re
import socket
import requests

from contextlib import closing

from tauk.enums import AttachmentTypes

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


def get_browser_debugger_address(driver):
    browser_name = driver.capabilities.get('browserName', '')
    if browser_name == 'chrome':
        return driver.capabilities['goog:chromeOptions']['debuggerAddress']
    elif browser_name == 'firefox':
        return driver.capabilities['moz:debuggerAddress']
    elif browser_name == 'msedge':
        return driver.capabilities['ms:edgeOptions']['debuggerAddress']
    else:
        return None


def get_open_port(port_range):
    for port in port_range:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex(('0.0.0.0', port)) != 0:
                return port
    return None


def shortened_json(json_text):
    json_text = re.sub(r'"screenshot": ".+?"', '"screenshot" : "stripped"', json_text, flags=re.DOTALL)
    json_text = re.sub(r'"view": ".+?", "', '"view" : "stripped", ', json_text, flags=re.DOTALL)
    json_text = re.sub(r'"log": \[.+?}\], "', '"log": ["stripped"], "', json_text, flags=re.DOTALL)
    return json_text


def attach_assistant_artifacts(assistant, test_case):
    browser_debugger_address = test_case.browser_debugger_address
    if assistant and assistant.config.is_cdp_capture_enabled():
        if assistant.is_running():
            connected_page = test_case.browser_debugger_page_id
            if connected_page:
                # Try and close browser connection
                try:  # If the browser already quit then close_page will throw an error
                    assistant.close_page(browser_debugger_address)
                except Exception:
                    logger.debug(f'[Assistant] Page {connected_page} was already closed')

            try:
                assistant.unregister_browser(browser_debugger_address)
            except Exception as ex:
                logger.warning(f'Failed to unregister browser for test [{test_case.method_name}]', exc_info=ex)

        # It's possible that assistant started and crashed before this point
        # So we want to be able to check if there are any logs if we have a valid page ID
        if test_case.browser_debugger_page_id:
            assistant_attachments = assistant.get_attachments(connected_page_id=test_case.browser_debugger_page_id)
            for file, file_type in assistant_attachments:
                try:
                    test_case.add_attachment(file, file_type)
                except Exception as ex:
                    logger.error(f'[Assistant] Failed to add attachment [{file_type}: {file}]', exc_info=ex)
        else:
            logger.warning(f'[Assistant] Page connection was never made for {test_case.browser_debugger_address}')
    else:
        logger.debug('[Assistant] Capture is disabled')


def upload_attachments(api, test_case):
    if len(test_case.attachments) == 0:
        logger.debug('No attachments to upload')
    for file_path, attachment_type in test_case.attachments:
        try:
            api.upload_attachment(file_path, attachment_type, test_case.id)
            # If it's an assistant attachment we should delete it after successful upload
            if AttachmentTypes.is_assistant_attachment(attachment_type):
                if os.path.exists(file_path):
                    logger.debug(f'Deleting assistant attachment {file_path}')
                    os.remove(file_path)
        except Exception as ex:
            logger.error(f'Failed to upload attachment {attachment_type}: {file_path}', exc_info=ex)
