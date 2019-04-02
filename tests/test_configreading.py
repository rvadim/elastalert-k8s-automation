from config import parse_config
from config import validate


class TestAdminConfig:

    def test_valid_config(self):
        errors = validate(parse_config('tests/fixtures/valid_config.yaml'))
        assert(len(list(errors)) == 0)

    def test_invalid_config(self):
        errors = list(validate(parse_config('tests/fixtures/invalid_config.yaml')))
        assert(str(errors[0]) == 'es_host in configuration is None, please specify es_host')
        assert(str(errors[1]) == 'es_port in configuration file is not in range(0), '
                                 'please specify es_port in range 1 < port < 65535')
        assert(len(errors) == 2)
