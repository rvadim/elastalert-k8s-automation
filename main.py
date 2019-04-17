import os
import sys

from kubernetes import config
import kubernetes.client
import yaml
import logging
from config import parse_config
from config import validate
from config import validate_user_rule
from config import get_env_vars_by_prefix

logging.basicConfig(level=os.environ.get('LOG_LEVEL', logging.INFO))
log = logging.getLogger(__name__)


def read_config_files(configuration):
    """
    Read configuration files from configmaps in all available namespaces
    :param configuration: Kubernetes client configuration
    :return: list of user elastalert rules
    """
    api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
    configmap_list = api_instance.list_config_map_for_all_namespaces(field_selector='metadata.name=elastalert-rules')

    user_configs = []
    for configmap in configmap_list:
        for rule_name in configmap.data:
            try:
                user_rule = yaml.safe_load(configmap.data[rule_name])
                errors = validate_user_rule(user_rule)
                if len(errors) != 0:
                    for error in errors:
                        log.error(error)
                    continue

                user_configs.append(user_rule)
            except yaml.YAMLError as e:
                log.error(f'Failed to parse configuration. {e}')

    return user_configs


def main():
    config_path = os.environ.get('CONFIG', 'config.yaml')
    log.info('Reading configuration file "{}"...', config_path)
    parsed_config = parse_config(config_path)
    parsed_config.update(get_env_vars_by_prefix())
    errors = validate(parsed_config)
    if len(errors) != 0:
        for error in errors:
            log.error(error)
        sys.exit(1)

    config.load_incluster_config()
    configuration = kubernetes.client.Configuration()
    read_config_files(configuration)


if __name__ == "__main__":
    main()
