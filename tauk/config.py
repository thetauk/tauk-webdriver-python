import os

from tauk.companion.config import CompanionConfig
from tauk.exceptions import TaukInvalidTypeException, TaukException


class TaukConfig:
    def __init__(self, api_token=None, project_id=None, multiprocess_run=None) -> None:
        # Default value for multiprocess_run should be false, however we have set it to None in the argument
        # because if no value is passed we should try reading from the environment variable
        if multiprocess_run is None:
            self._multiprocess_run = os.getenv('TAUK_MULTI_PROCESS', '').lower() == 'true'
        else:
            self._multiprocess_run = multiprocess_run if isinstance(multiprocess_run, bool) else False
        self._api_token = self._get_value_from_property_or_env(api_token, 'TAUK_API_TOKEN')
        self._project_id = self._get_value_from_property_or_env(project_id, 'TAUK_PROJECT_ID')

        self._api_url = os.environ.get('TAUK_API_URL', 'https://www.tauk.com/api/v1')
        self._cleanup_exec_context = True
        self._companion_config: CompanionConfig | None = None

    def _get_value_from_property_or_env(self, prop, env_var):
        if prop:
            return prop
        elif os.getenv(env_var):
            return os.getenv(env_var)
        elif self.multiprocess_run:
            # Multiprocess runs don't need API Token/ Project ID because it could be read from the exec file
            return None

        raise TaukException(f'could not find a valid environment variable ${env_var}')

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

    @property
    def cleanup_exec_context(self):
        return self._cleanup_exec_context

    @cleanup_exec_context.setter
    def cleanup_exec_context(self, val: bool):
        self._validate_type(val, bool)
        self._cleanup_exec_context = val

    @property
    def companion_config(self):
        return self._companion_config

    @companion_config.setter
    def companion_config(self, val: CompanionConfig):
        self._validate_type(val, CompanionConfig)
        self._companion_config = val

    @staticmethod
    def _validate_type(val, expected_type):
        if not isinstance(val, expected_type):
            raise TaukInvalidTypeException(f'property type must be {expected_type}')

    def is_companion_enabled(self):
        return self.companion_config is not None

    def __str__(self):
        return f'TaukConfig: APIToken={self.api_token}, ProjectID={self.project_id}, API_URL={self.api_url}, ' \
               f'MultiprocessRun={self.multiprocess_run}, CleanupExecContext={self.cleanup_exec_context}, ' \
               f'Companion: {self.companion_config}'
