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


def install_companion(url, ver):
    print_verbose(f'Installing tauk-companion from {url}')
    binaries_home = os.path.join(Path.home(), '.tauk', 'binaries')
    companion_file_path = os.path.join(binaries_home, 'tauk-companion.tgz')
    binary_path = os.path.join(binaries_home, f'tauk-companion-{get_os_name()}-{get_architecture_name()}')
    new_binary_path = binary_path.replace(f'-{get_os_name()}-{get_architecture_name()}', '')

    if not os.path.exists(binaries_home):
        os.makedirs(binaries_home)

    download_url = f'{url}/companion/binary?version={ver}&os={get_os_name()}&arch={get_architecture_name()}'
    print_verbose(f'Downloading binary {download_url}')
    response = requests.get(download_url, allow_redirects=True, timeout=180, stream=True)
    total_size_bytes = int(response.headers.get('content-length', 0))
    with tqdm.wrapattr(open(companion_file_path, 'wb'), "write", unit='iB', unit_scale=True, unit_divisor=1024,
                       miniters=1, desc=f'Downloading Binary: {new_binary_path}', total=total_size_bytes) as file:
        for chunk in response.iter_content(chunk_size=4096):
            file.write(chunk)

    print_verbose(f'Extracting tar file {companion_file_path}')
    import tarfile
    with tarfile.open(companion_file_path) as file:
        file.extractall(binaries_home)

    try:
        os.rename(binary_path, new_binary_path)
        os.remove(companion_file_path)

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

    companion_parser.add_argument('-i', '--install', dest='install', action=argparse.BooleanOptionalAction,
                                  help='Install tauk companion')
    companion_parser.add_argument('-u', '--download-url', dest='url', type=str, metavar='DOWNLOAD_URL', required=True,
                                  help='Companion download URL')
    companion_parser.add_argument('-v', '--version', dest='version', type=str,
                                  help='[Unstable] Version of companion to download')
    args = parser.parse_args()

    verbose = args.verbose

    if args.install:
        version = '0.2.2' if not args.version else args.version
        install_companion(args.url, version)
    else:
        print(parser.format_help())
