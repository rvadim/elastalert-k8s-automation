import functools
import os

import jsonschema
import yaml


class ConfigurationError(Exception):
    pass


class PropertyNotExistError(ConfigurationError):
    def __init__(self, prop_name: str, *args):
        self.message = 'Required property \'' + prop_name + '\' is not specified.'
        super().__init__(self.message, *args)


class PropertyFormatError(ConfigurationError):
    def __init__(self, prop_name: str, incomming_message: str, *args):
        self.message = 'Validation of property \'' + \
                       prop_name + '\' failed.\n\t' + \
                       incomming_message
        super().__init__(self.message, *args)


def validators():
    registry = {}

    def reg(func):
        registry[func.__name__] = func
        return func

    reg.all = registry
    return reg


validator = validators()
rule_validator = validators()


def uses_adm_schema(func):
    """
    Decorator for parsing validation schema only once
    """
    first_run = True

    @functools.wraps(func)
    def inner(*args, **kwargs):
        nonlocal first_run

        if first_run:
            inner.schema = parse_config('schemas/admin_validation_schema.yaml')
            first_run = False
        result = func(*args, **kwargs)
        return result

    return inner


def parse_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def get_env_vars_by_prefix():
    env_vars = os.environ
    es_vars = dict()
    prefix = 'EA_'
    for key, value in env_vars.items():
        if key.startswith(prefix) and len(key) > len(prefix):
            es_vars[key[len(prefix):-1]] = value
    return es_vars


def validate(config):
    errors = []
    for _, v in validator.all.items():
        errors.append(v(config))
    return filter(lambda x: x is not None, errors)


@uses_adm_schema
def check_property_format(config, prop_name):
    """
    Checks format of config's property by validating with validation_schema
    :param config: admin config to check
    :param prop_name: property format to check
    :return: PropertyFormatError with property name and jsonschema.exceptions.ValidationError message \
            if format does not correspond to validation schema format
    """
    validation_schema = check_property_format.schema
    try:
        jsonschema.validate(config[prop_name], validation_schema['properties'][prop_name])
        return None
    except jsonschema.exceptions.ValidationError as sch_val_er:
        return PropertyFormatError(prop_name, sch_val_er.args[0])


@validator
def check_es_host(config):
    prop_name = 'es_host'
    if not config.get(prop_name):
        return PropertyNotExistError(prop_name)

    format_check_err = check_property_format(config, prop_name)
    if format_check_err:
        return format_check_err


@validator
def check_es_port(config):
    prop_name = 'es_port'
    port = config.get(prop_name)
    if not port:
        return PropertyNotExistError(prop_name)

    format_check_err = check_property_format(config, prop_name)
    if format_check_err:
        return format_check_err

    if port < 1 or port > 65535:
        return ConfigurationError(
            f'Property \'es_port\' value={port} is out of range, '
            f'please specify \'es_port\' in range 1 < port < 65535')


@validator
def check_password(config):
    prop_name = 'es_password'
    if not config.get(prop_name):
        return None
    return check_property_format(config, prop_name)


@validator
def check_rules_folder(config):
    prop_name = 'rules_folder'
    if not config.get(prop_name):
        return PropertyNotExistError(prop_name)
    return check_property_format(config, prop_name)


@validator
def check_run_every(config):
    prop_name = 'run_every'
    if not config.get(prop_name):
        return PropertyNotExistError(prop_name)
    return check_property_format(config, prop_name)


@validator
def check_buffer_time(config):
    prop_name = 'buffer_time'
    if not config.get(prop_name):
        return PropertyNotExistError(prop_name)
    return check_property_format(config, prop_name)


@validator
def check_writeback_index(config):
    prop_name = 'writeback_index'
    if not config.get(prop_name):
        return PropertyNotExistError(prop_name)
    return check_property_format(config, prop_name)


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
