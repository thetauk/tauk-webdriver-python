"""Main entry point"""
import argparse
import logging
import os.path
import platform
import sys
import traceback
from pathlib import Path

import requests
from tqdm import tqdm


def print_verbose(line, exec_info=None):
    if verbose:
        print(line)
        if exec_info:
            traceback.print_exception(exec_info)


def get_os_name():
    return platform.system().lower()


def get_architecture_name():
    return platform.machine().lower()


def install_companion(api_token, ver, url=None):
    download_api_url = f'https://www.tauk.com/api/v1/companion/binary' if url is None else url
    download_api_url = f'{download_api_url}?version={ver}&os={get_os_name()}&arch={get_architecture_name()}'

    print_verbose(f'Installing tauk-companion from {download_api_url}')
    binaries_home = os.path.join(Path.home(), '.tauk', 'binaries')
    companion_tgz_path = os.path.join(binaries_home, 'tauk-companion.tgz')
    binary_path = os.path.join(binaries_home, f'tauk-companion-{get_os_name()}-{get_architecture_name()}')
    new_binary_path = binary_path.replace(f'-{get_os_name()}-{get_architecture_name()}', '')

    if not os.path.exists(binaries_home):
        os.makedirs(binaries_home)

    header = {'Authorization': f'Bearer {api_token}'}
    response = requests.get(download_api_url, headers=header)
    if not response.ok:
        print_verbose(f'[{response.status_code}] {response.text}')
        print('Failed to download tauk-companion. Please verify if your API token is correct')
        sys.exit(1)

    s3_download_url = response.json()['url']

    print_verbose(f'Downloading binary from S3: {s3_download_url}')
    response = requests.get(s3_download_url, allow_redirects=True, timeout=180, stream=True)
    total_size_bytes = int(response.headers.get('content-length', 0))
    with tqdm.wrapattr(open(companion_tgz_path, 'wb'), "write", unit='iB', unit_scale=True, unit_divisor=1024,
                       miniters=1, desc=f'Downloading Binary: {new_binary_path}', total=total_size_bytes) as file:
        for chunk in response.iter_content(chunk_size=4096):
            file.write(chunk)

    print_verbose(f'Extracting tar file {companion_tgz_path}')
    import tarfile
    with tarfile.open(companion_tgz_path) as file:
        file.extractall(binaries_home)

    try:
        os.rename(binary_path, new_binary_path)
        os.remove(companion_tgz_path)

        if get_os_name() == 'darwin':
            exit_code = os.system(f'xattr -r -d com.apple.quarantine {new_binary_path}')
            if exit_code != 0:
                print('Failed to remove quarantine flag')
    except Exception as ex:
        print(f'Failed to extract tauk binary')
        print_verbose(f'Failed to extract {binary_path}', exec_info=ex)


if sys.argv[0].endswith("__main__.py"):
    logger = logging.getLogger('tauk')
    parser = argparse.ArgumentParser(prog='tauk')
    parser.add_argument('--verbose', action=argparse.BooleanOptionalAction, help='Print verbose logs')
    subparser = parser.add_subparsers()
    companion_parser = subparser.add_parser('companion')
    cleanup_parser = subparser.add_parser('cleanup')  # TODO: Implement cleanup

    companion_parser.add_argument('-t', '--api-token', dest='token', type=str, metavar='API_TOKEN', required=True,
                                  help='Companion download URL')
    companion_parser.add_argument('-v', '--version', dest='version', type=str,
                                  help='[Unstable] Version of companion to download')
    companion_parser.add_argument('-i', '--install', dest='install', action=argparse.BooleanOptionalAction,
                                  help='Install tauk companion')
    args = parser.parse_args()

    verbose = args.verbose

    if args.install:
        # We tie a  companion version for every release
        install_companion(args.token, '0.2.2' if not args.version else args.version)
    else:
        print(parser.format_help())
