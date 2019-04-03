import functools
import jsonschema
import yaml


class ConfigurationError(Exception):
    pass


class PropertyNotExistError(ConfigurationError):
    def __init__(self, prop_name: str, *args):
        self.message = 'Required property \'' + prop_name + '\' is not specified.'
        super().__init__(self.message, *args)


class PropertyFormatError(ConfigurationError):
    def __init__(self, prop_name: str, inc_mes: str, *args):
        self.message = 'Failed validating property \'' + prop_name + '\'.\n\t' + inc_mes
        super().__init__(self.message, *args)


def validators():
    registry = {}

    def reg(func):
        registry[func.__name__] = func
        return func

    reg.all = registry
    return reg


validator = validators()


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
        return ConfigurationError(f'Property \'es_port\' value={port} is out of range, '
                                  f'please specify \'es_port\' in range 1 < port < 65535')


@validator
def check_rules_folder(config):
    prop_name = 'rules_folder'
    if not config.get(prop_name):
        return PropertyNotExistError(prop_name)

    format_check_err = check_property_format(config, prop_name)
    if format_check_err:
        return format_check_err


@validator
def check_run_every(config):
    prop_name = 'run_every'
    if not config.get(prop_name):
        return PropertyNotExistError(prop_name)

    format_check_err = check_property_format(config, prop_name)
    if format_check_err:
        return format_check_err


@validator
def check_buffer_time(config):
    prop_name = 'buffer_time'
    if not config.get(prop_name):
        return PropertyNotExistError(prop_name)

    format_check_err = check_property_format(config, prop_name)
    if format_check_err:
        return format_check_err


@validator
def check_writeback_index(config):
    prop_name = 'writeback_index'
    if not config.get(prop_name):
        return PropertyNotExistError(prop_name)

    format_check_err = check_property_format(config, prop_name)
    if format_check_err:
        return format_check_err
