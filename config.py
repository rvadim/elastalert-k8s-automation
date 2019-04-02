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
