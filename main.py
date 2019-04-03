from kubernetes import config
import kubernetes.client
import yaml
import logging
from jsonschema import validate, ValidationError

LOGGER = logging.getLogger()


class IncorrectConfigException(Exception):
    def __init__(self, message):
        self.message = message


def check_user_config(user_config):
    with open('./schemas/user_config_schema.yaml', 'r') as schema_file:
        user_config_schema = yaml.load(schema_file)

    validate(user_config, user_config_schema)


def read_user_config(config_file):
    """
    Read user elastalert configuration
    :param config_file: configuration file
    :return: user elastalert configuration
    """
    user_config = yaml.load(config_file)
    check_user_config(user_config)

    return user_config


def read_config_files(configuration):
    """
    Read configuration files from configmaps in all available namespaces
    :param configuration: Kubernetes client configuration
    :return: list of user elastalert configurations
    """
    api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
    configmap_list = api_instance.list_config_map_for_all_namespaces()

    user_configs = []
    for configmap in configmap_list:
        try:
            user_config = read_user_config(configmap.data)
            user_configs.append(user_config)
        except ValidationError as e:
            LOGGER.exception(e.message)
            continue

    return user_configs


def main():
    config.load_incluster_config()
    configuration = kubernetes.client.Configuration()
    user_configs = read_config_files(configuration)


if __name__ == "__main__":
    main()
