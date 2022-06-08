"""Main entry point"""
import argparse
import logging
import os.path
import platform
import sys
import traceback
import requests

from pathlib import Path
from tqdm import tqdm

TAUK_HOME = os.path.join(Path.home(), '.tauk')


def print_verbose(line, exec_info=None):
    if verbose:
        print(line)
        if exec_info:
            traceback.print_exception(exec_info)


def get_os_name():
    return platform.system().lower()


def get_architecture_name():
    machine = platform.machine().lower()
    return 'amd64' if machine == 'x86_64' else machine


def install_assistant(api_token, ver, url=None):
    download_api_url = f'https://www.tauk.com/api/v1/assistant/binary' if url is None else url
    download_api_url = f'{download_api_url}?version={ver}&os={get_os_name()}&arch={get_architecture_name()}'

    print_verbose(f'Installing tauk-assistant from {download_api_url}')
    binaries_home = os.path.join(TAUK_HOME, 'binaries')
    assistant_tgz_path = os.path.join(binaries_home, 'tauk-assistant.tgz')
    binary_path = os.path.join(binaries_home, f'tauk-assistant-{get_os_name()}-{get_architecture_name()}')
    new_binary_path = binary_path.replace(f'-{get_os_name()}-{get_architecture_name()}', '')

    if not os.path.exists(binaries_home):
        os.makedirs(binaries_home)

    header = {'Authorization': f'Bearer {api_token}'}
    response = requests.get(download_api_url, headers=header)
    if not response.ok:
        print_verbose(f'[{response.status_code}] {response.text}')
        print('Failed to download tauk-assistant. Please verify if your API token is correct')
        sys.exit(1)

    s3_download_url = response.json()['url']

    print_verbose(f'Downloading binary from S3: {s3_download_url}')
    response = requests.get(s3_download_url, allow_redirects=True, timeout=180, stream=True)
    total_size_bytes = int(response.headers.get('content-length', 0))
    with tqdm.wrapattr(open(assistant_tgz_path, 'wb'), "write", unit='iB', unit_scale=True, unit_divisor=1024,
                       miniters=1, desc=f'Downloading Binary: {new_binary_path}', total=total_size_bytes) as file:
        for chunk in response.iter_content(chunk_size=4096):
            file.write(chunk)

    print_verbose(f'Extracting tar file {assistant_tgz_path}')
    import tarfile
    with tarfile.open(assistant_tgz_path) as file:
        file.extractall(binaries_home)

    try:
        os.rename(binary_path, new_binary_path)
        os.remove(assistant_tgz_path)

        if get_os_name() == 'darwin':
            exit_code = os.system(f'xattr -r -d com.apple.quarantine {new_binary_path}')
            if exit_code != 0:
                print('Failed to remove quarantine flag')
    except Exception as ex:
        print(f'Failed to extract tauk binary')
        print_verbose(f'Failed to extract {binary_path}', exec_info=ex)


def print_files_in_tauk_home():
    paths = list(Path(TAUK_HOME).rglob("*"))
    logs = []
    binaries = []
    assistant = []
    others = []
    for path in paths:
        if Path(path).name in ['.DS_Store', 'logs', 'binaries']:
            continue
        elif str(path).startswith(f'{os.path.join(TAUK_HOME, "logs")}'):
            logs.append(path)
        elif str(path).startswith(f'{os.path.join(TAUK_HOME, "binaries")}'):
            binaries.append(path)
        else:
            others.append(path)

    print('Logs:')
    for log in logs:
        print(f' {log}\t{log.stat().st_size}')

    print('Binaries:')
    for binary in binaries:
        print(f' {binary}\t{binary.stat().st_size}')

    print('Others:')
    for other in others:
        print(f' {other}\t{other.stat().st_size}')


if sys.argv[0].endswith("__main__.py"):
    logger = logging.getLogger('tauk')
    parser = argparse.ArgumentParser(prog='tauk')
    parser.add_argument('--verbose', action=argparse.BooleanOptionalAction, help='Print verbose logs')
    subparser = parser.add_subparsers(help='commands', dest='command', required=True)
    assistant_parser = subparser.add_parser('assistant')
    assistant_parser.add_argument('-t', '--api-token', dest='token', type=str, metavar='API_TOKEN', required=True,
                                  help='Assistant download URL')
    assistant_parser.add_argument('-v', '--version', dest='version', type=str,
                                  help='[Unstable] Version of assistant to download')
    assistant_parser.add_argument('-i', '--install', dest='install', action=argparse.BooleanOptionalAction,
                                  help='Install tauk assistant')

    cleanup_parser = subparser.add_parser('cleanup')
    cleanup_parser.add_argument('-l', '--list', dest='list', action=argparse.BooleanOptionalAction,
                                help='list all the files in tauk home directory')

    args = parser.parse_args()

    verbose = args.verbose

    if args.command == 'assistant':
        if args.install:
            # We tie an assistant version to every release
            install_assistant(args.token, '0.2.5' if not args.version else args.version)
            sys.exit(0)
    elif args.command == 'cleanup':
        if args.list:
            print_files_in_tauk_home()
            sys.exit(0)

    print(parser.format_help())
