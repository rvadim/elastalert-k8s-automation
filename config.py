import yaml


class ConfigurationError(Exception):
    pass


def validators():
    registry = {}

    def reg(func):
        registry[func.__name__] = func
        return func
    reg.all = registry
    return reg


validator = validators()
rule_validator = validators()


def parse_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def validate(config):
    errors = []
    for _, v in validator.all.items():
        errors.append(v(config))
    return filter(lambda x: x is not None, errors)


@validator
def check_es_host(config):
    if config.get('es_host') is None:
        return ConfigurationError(
            'es_host in configuration is None, please specify es_host')
    if config.get('es_host') == '':
        return ConfigurationError(
            'es_host in configuration is empty string, please specify es_host')


@validator
def check_es_port(config):
    port = config.get('es_port')
    if port is None:
        return ConfigurationError(
            'es_port in configuration file is None, please specify es_port')

    if not isinstance(port, int):
        return ConfigurationError(
            'es_port in configuration file is not int, '
            'please specify es_port in range 1 < port < 65535, '
            'type: {}'.format(type(port)))

    if port < 1 or port > 65535:
        return ConfigurationError(
            'es_port in configuration file is not in range({}), '
            'please specify es_port in range 1 < port < 65535'.format(port))


def check_required(value, name):
    if value is None:
        raise ConfigurationError(
            f'{name} in configuration file is None, please specify {name}')


def check_type(value, v_type, name):
    if not isinstance(value, v_type):
        raise ConfigurationError(
            f'{name} in configuration file is not {v_type}, '
            f'type: {type(value)}')


@rule_validator
def check_index(config):
    index = config.get('index')

    try:
        check_required(index, 'index')
        check_type(index, str, 'index')
    except ConfigurationError as e:
        return e

    if config.get('index') == '':
        return ConfigurationError(
            'index in configuration is empty string, please specify index')


@rule_validator
def check_rule_type(config):
    correct_types = {'any', 'blacklist', 'whitelist', 'change', 'frequency', 'spike',
                     'flatline', 'new_term', 'cardinality', 'metric_aggregation', 'percentage_match'}
    rule_type = config.get('type')

    try:
        check_required(rule_type, 'type')
        check_type(rule_type, str, 'type')
    except ConfigurationError as e:
        return e

    if rule_type not in correct_types:
        return ConfigurationError(
            f'Elastalert rule type {rule_type} in configuration is incorrect.'
            f'Type must be one of {", ".join(correct_types)}.')


def validate_user_rule(user_rule):
    errors = []
    for _, v in rule_validator.all.items():
        errors.append(v(user_rule))
    return filter(lambda x: x is not None, errors)
