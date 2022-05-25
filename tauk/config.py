import os

from tauk.companion.config import CompanionConfig
from tauk.exceptions import TaukInvalidTypeException, TaukException


class TaukConfig:
    def __init__(self, api_token=None, project_id=None) -> None:
        self._multiprocess_run = self._get_run_type()
        self._fetch_api_token(api_token)
        self._fetch_project_id(project_id)

        self._api_url = os.environ.get('TAUK_API_URL', 'https://www.tauk.com/api/v1')
        self._cleanup_exec_context = True
        self._companion: CompanionConfig | None = None

    def _fetch_api_token(self, api_token):
        env_var = 'TAUK_API_TOKEN'
        if api_token:
            self._api_token = api_token
        elif os.getenv(env_var):
            self._api_token = os.getenv(env_var)
        elif not self.multiprocess_run:
            raise TaukException(f'could not find a valid API token in environment variable ${env_var}')

    def _fetch_project_id(self, project_id):
        env_var = 'TAUK_PROJECT_ID'
        if project_id:
            self._project_id = project_id
        elif os.getenv(env_var):
            self._project_id = os.getenv(env_var)
        elif not self.multiprocess_run:
            raise TaukException(f'could not find a valid Project ID in environment variable ${env_var}')

    def _get_run_type(self):
        return (os.getenv('TAUK_MULTI_PROCESS').lower() == 'true') if os.getenv('TAUK_MULTI_PROCESS') else False

    @property
    def api_token(self):
        return self._api_token

    @property
    def project_id(self):
        return self._project_id

    @property
    def api_url(self):
        return self._api_url

    @property
    def multiprocess_run(self):
        return self._multiprocess_run

    @multiprocess_run.setter
    def multiprocess_run(self, val: bool):
        self._validate_type(val, bool)
        self._multiprocess_run = val

    @property
    def cleanup_exec_context(self):
        return self._cleanup_exec_context

    @cleanup_exec_context.setter
    def cleanup_exec_context(self, val: bool):
        self._validate_type(val, bool)
        self._cleanup_exec_context = val

    @property
    def companion(self):
        return self._companion

    @companion.setter
    def companion(self, val: CompanionConfig):
        self._validate_type(val, CompanionConfig)
        self._companion = CompanionConfig

    @staticmethod
    def _validate_type(val, expected_type):
        if not isinstance(val, expected_type):
            raise TaukInvalidTypeException(f'property type must be {expected_type}')

    def is_companion_enabled(self):
        return self.companion is not None

    def __str__(self):
        return f'TaukConfig: APIToken={self.api_token}, ProjectID={self.project_id}, API_URL={self.api_url}, ' \
               f'MultiprocessRun={self.multiprocess_run}, CleanupExecContext={self.cleanup_exec_context}, ' \
               f'Companion: {self.companion}'
