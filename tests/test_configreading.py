from config import ConfigurationError
from config import PropertyFormatError
from config import PropertyNotExistError
from config import parse_config
from config import validate


class TestAdminConfig:

    def test_valid_config(self):
        errors = validate(parse_config('tests/fixtures/valid_config.yaml'))
        assert (len(list(errors)) == 0)

    def test_invalid_config(self):
        errors = list(validate(parse_config('tests/fixtures/invalid_config.yaml')))
        assert (len(errors) == 6)
        assert isinstance(errors[0], PropertyNotExistError)
        assert isinstance(errors[1], ConfigurationError)
        assert isinstance(errors[2], PropertyFormatError)
        assert isinstance(errors[3], PropertyFormatError)
        assert isinstance(errors[4], PropertyFormatError)
        assert isinstance(errors[5], PropertyFormatError)
