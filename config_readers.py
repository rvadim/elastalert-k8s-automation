import logging
import os
import sys
from abc import abstractmethod

import kubernetes.client
import yaml

from config import get_env_vars_by_prefix
from config import parse_config
from config import validate
from config import validate_user_rule

log = logging.getLogger("__main__")


class BaseConfigReader:
    """
    Base class for user config readers with common interface
    """
    def _read_user_rule(self, rule_yaml):
        """
        Parse user rule and return result if parsing was successful
        :param rule_yaml: file to parse
        :return: dictionary with parsing results
        """
        try:
            parsed_user_rule = yaml.safe_load(rule_yaml)
            return parsed_user_rule
        except yaml.YAMLError as e:
            log.error(f'Failed to parse configuration. {e}')
        return None

    def _validate_user_rule(self, parsed_user_rule):
        """
        Validate given parsed config
        :param parsed_user_rule:
        :return:
        """
        if parsed_user_rule is None:
            return None
        errors = list(validate_user_rule(parsed_user_rule))
        if len(errors) != 0:
            for error in errors:
                log.error(error)
            return None
        return parsed_user_rule

    @abstractmethod
    def get_config_files(self):
        pass


class RemoteUserConfigReader(BaseConfigReader):
    """
    Class for reading user configuration files in kubernetes cluster
    """
    def __init__(self):
        pass

    def _get_configmap_list(self):
        """
        Get configmaps in all available namespaces
        :return: list of configmaps
        """
        api_instance = kubernetes.client.CoreV1Api()
        namespaces = api_instance.list_namespace()
        configmap_list = []

        for namespace in namespaces.items:
            try:
                configmap_list.append(
                    api_instance.read_namespaced_config_map('elastalert-rules', namespace.metadata.name))
            except Exception as e:
                log.warning(e)
        return configmap_list

    def get_config_files(self):
        """
        Read configuration files from configmaps
        :return: list of user elastalert rules
        """
        log.info('Reading users configuration files')

        configmap_list = self._get_configmap_list()

        user_configs = []
        for configmap in configmap_list:
            for rule_name in configmap.data:
                log.info(f'Reading user rule {rule_name} from configmap {configmap.metadata.name}'
                         f' in namespace {configmap.metadata.namespace}')
                user_rule = self._read_user_rule(configmap.data[rule_name])
                user_rule = self._validate_user_rule(user_rule)
                if user_rule is not None:
                    user_configs.append(user_rule)

        return user_configs


class LocalUserConfigReader(BaseConfigReader):
    """
    Class for reading user configuration files locally from disk
    """
    def __init__(self, directory):
        self.directory = directory

    def get_config_files(self):
        """
        Read configuration files from local directory
        :return: list of user elastalert rules
        """
        user_configs = []
        for file in os.listdir(self.directory):
            f_path = os.path.join(self.directory, file)
            if os.path.isdir(file):
                continue
            with open(f_path, 'r') as f:
                log.info(f'Reading user rule from file {file}')
                user_rule = self._read_user_rule(f)
                user_rule = self._validate_user_rule(user_rule)
                if user_rule is not None:
                    user_configs.append(user_rule)

        return user_configs


def get_admin_config_file(config_path):
    """
    Get raw admin config file and validate it
    :param config_path: path to config file
    :return: parsed and validated config file
    """
    log.info(f'Reading configuration file "{config_path}"...')
    parsed_config = parse_config(config_path)
    parsed_config.update(get_env_vars_by_prefix())
    errors = list(validate(parsed_config))

    if len(errors) != 0:
        for error in errors:
            log.error(error)
        sys.exit(1)
    return parsed_config
