import os
from kubernetes import config
import kubernetes.client
import yaml
import logging
from config import validate_user_rule

logging.basicConfig(level=os.environ.get('LOG_LEVEL', logging.INFO))
log = logging.getLogger(__name__)


def read_config_files(configuration):
    """
    Read configuration files from configmaps in all available namespaces
    :param configuration: Kubernetes client configuration
    :return: list of user elastalert rules
    """
    api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
    configmap_list = api_instance.list_config_map_for_all_namespaces()

    user_configs = []
    for configmap in configmap_list:
        if configmap.metadata.name == 'elastalert-rules':
            for rule_name in configmap.data:
                user_rule = yaml.safe_load(configmap.data[rule_name])
                errors = validate_user_rule(user_rule)
                if len(errors) != 0:
                    for error in errors:
                        log.error(error)
                    continue

                user_configs.append(user_rule)

    return user_configs


def main():
    config.load_incluster_config()
    configuration = kubernetes.client.Configuration()
    user_configs = read_config_files(configuration)


if __name__ == "__main__":
    main()
