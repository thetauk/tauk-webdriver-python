import logging
import os
import re
import socket
import requests

from contextlib import closing

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


def attach_companion_artifacts(companion, test_case):
    browser_debugger_address = test_case.browser_debugger_address
    if companion and companion.config.is_cdp_capture_enabled():
        if companion.is_running():
            connected_page = test_case.browser_debugger_page_id
            if connected_page:
                # Try and close browser connection
                # If the browser already quit then close_page with throw an error
                try:
                    companion.close_page(browser_debugger_address)
                except Exception:
                    logger.debug(f'[Companion] Page {connected_page} was already closed')

        companion_attachments = companion.get_attachments(browser_debugger_address)
        for attachment_file, attachment_type in companion_attachments:
            try:
                test_case.add_attachment(attachment_file, attachment_type)
            except Exception as ex:
                logger.error(f'[Companion] Failed to add companion attachment [{attachment_type}: {attachment_file}]',
                             exc_info=ex)
    else:
        logger.debug('[Companion] Capture is disabled')


def upload_attachments(api, test_case):
    if len(test_case.attachments) == 0:
        logger.debug('No attachments to upload')
    for file_path, attachment_type in test_case.attachments:
        try:
            api.upload_attachment(file_path, attachment_type, test_case.id)
            # If it's a companion attachment we should delete it after successful upload
            if attachment_type.is_companion_attachment():
                if os.path.exists(file_path):
                    logger.debug(f'Deleting companion attachment {file_path}')
                    os.remove(file_path)
        except Exception as ex:
            logger.error(f'Failed to upload attachment {attachment_type}: {file_path}', exc_info=ex)
