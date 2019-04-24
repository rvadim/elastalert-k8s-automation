import os
import sys
import time

from kubernetes import config
import kubernetes.client
import yaml
import logging
from jinja2 import FileSystemLoader, Environment
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
            log.info(f'User rule:\n{yaml.dump(user_rule)}')
            log.info(f'Reading user rule {rule_name} from configmap {configmap.metadata.name}'
                     f' in namespace {configmap.metadata.namespace}')
            user_rule = read_user_rule(configmap.data[rule_name])
            if user_rule is not None:
                user_configs.append(user_rule)

    return user_configs


def get_config(config_path):
    log.info(f'Reading configuration file "{config_path}"...')
    parsed_config = parse_config(config_path)
    parsed_config.update(get_env_vars_by_prefix())
    errors = list(validate(parsed_config))

    if len(errors) != 0:
        for error in errors:
            log.error(error)
        sys.exit(1)
    return parsed_config


def read_user_rule(rule_yaml):
    try:
        user_rule = yaml.safe_load(rule_yaml)
        errors = list(validate_user_rule(user_rule))
        if len(errors) != 0:
            for error in errors:
                log.error(error)
            return None

        return user_rule
    except yaml.YAMLError as e:
        log.error(f'Failed to parse configuration. {e}')


def read_local_config_files(directory):
    """
    Read configuration files from local directory
    :param directory: local directory
    :return: list of user elastalert rules
    """
    user_configs = []
    for file in os.listdir(directory):
        f_path = os.path.join(directory, file)
        if os.path.isdir(file):
            continue
        with open(f_path, 'r') as f:
            log.info(f'Reading user rule from file {file}')
            user_rule = read_user_rule(f)
            if user_rule is not None:
                user_configs.append(user_rule)

    return user_configs


def generate_config(env, template_name, context):
    template = env.get_template(template_name)
    return template.render(context)


def generate_ea_rules(user_configs, env):
    ea_rules = []
    for conf in user_configs:
        extended_conf = dict(conf)
        extended_conf.update(get_env_vars_by_prefix())
        ea_rules.append(generate_config(env, 'ea_rule.yaml.j2', extended_conf))
    return ea_rules


def main():
    local_run = os.environ.get('LOCAL_RUN') == '1'
    config_dir = os.environ.get('CONFIG_DIR', './eka/')
    ea_config_path = os.environ.get('EA_CONFIG_DIR', './config/')
    context = get_config(os.path.join(config_dir, 'config.yaml'))
    user_rules_directory = os.path.join(ea_config_path, 'rules')
    context['rules_folder'] = user_rules_directory

    env = Environment(loader=FileSystemLoader('templates'))
    with open(os.path.join(ea_config_path, 'config.yaml'), 'w') as f:
        f.write(generate_config(env, 'ea_config.yaml.j2', context))

    if not local_run:
        configuration = config.load_incluster_config()

    while True:
        if not os.path.exists(user_rules_directory):
            os.makedirs(user_rules_directory, 755)
        # Drop all files from user rules directory
        for f in os.listdir(user_rules_directory):
            f_path = os.path.join(user_rules_directory, f)
            os.remove(f_path)

        if local_run:
            user_configs = read_local_config_files(os.path.join(config_dir, 'rules'))
        else:
            user_configs = read_config_files(configuration)

        ea_rules = generate_ea_rules(user_configs, env)

        for i, rule in enumerate(ea_rules):
            with open(os.path.join(user_rules_directory, f'rule_{i}.yaml'), 'w') as output:
                output.write(rule)

        time.sleep(60)


if __name__ == "__main__":
    main()
