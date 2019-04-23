import os
import sys
import time

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
    log.info('Reading users configuration files')

    api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
    configmap_list = api_instance.list_config_map_for_all_namespaces(field_selector='metadata.name=elastalert-rules')

    user_configs = []
    for configmap in configmap_list.items:
        for rule_name in configmap.data:
            try:
                log.info(f'Reading user rule {rule_name} from configmap {configmap.metadata.name}'
                         f' in namespace {configmap.metadata.namespace}')
                user_rule = yaml.safe_load(configmap.data[rule_name])
                errors = list(validate_user_rule(user_rule))
                if len(errors) != 0:
                    for error in errors:
                        log.error(error)
                    continue

                log.info(f'User rule:\n{yaml.dump(user_rule)}')

                user_configs.append(user_rule)
            except yaml.YAMLError as e:
                log.error(f'Failed to parse configuration. {e}')

    return user_configs


def dump_config(config_data, filename):
    with open(filename, 'w') as f:
        yaml.dump(config_data, f)


def main():
    config_path = os.environ.get('CONFIG', 'config.yaml')
    log.info(f'Reading configuration file "{config_path}"...')
    parsed_config = parse_config(config_path)
    parsed_config.update(get_env_vars_by_prefix())
    errors = list(validate(parsed_config))

    if len(errors) != 0:
        for error in errors:
            log.error(error)
        sys.exit(1)

    user_rules_directory = parsed_config['rules_folder']

    configuration = config.load_incluster_config()

    while True:
        # Drop all files from user rules directory
        for f in os.listdir(user_rules_directory):
            f_path = os.path.join(user_rules_directory, f)
            os.remove(f_path)

        user_rules = read_config_files(configuration)

        for i, rule in enumerate(user_rules):
            dump_config(rule, os.path.join(user_rules_directory, f'config_{i}.yaml'))

        time.sleep(60)


if __name__ == "__main__":
    main()
