import pytest
import yaml
from jsonschema import ValidationError
from copy import copy

from main import read_user_config


class TestUserConfig:
    properties = ['es_host', 'es_port', 'index', 'type', 'alert']

    def build_test_config(self):
        test_config = {}
        test_config['es_host'] = '127.0.0.1'
        test_config['es_port'] = 80
        test_config['index'] = 'test_index'
        test_config['type'] = 'type'
        test_config['alert'] = 'email'

        return test_config

    def test_correct_config(self):
        test_config = yaml.dump(self.build_test_config())
        read_user_config(test_config)

    def test_missing_required_property(self):
        test_config = self.build_test_config()

        for p in TestUserConfig.properties:
            current_config = copy(test_config)
            del current_config[p]
            current_config = yaml.dump(current_config)

            with pytest.raises(ValidationError) as excinfo:
                read_user_config(current_config)

            assert f"'{p}' is a required property" in str(excinfo.value)

    def test_incorrect_property_type(self):
        test_config = self.build_test_config()

        for p in TestUserConfig.properties:
            current_config = copy(test_config)
            current_config[p] = 0.1
            current_config = yaml.dump(current_config)

            with pytest.raises(ValidationError) as excinfo:
                read_user_config(current_config)

            assert f"Failed validating 'type' in schema['properties']['{p}']" in str(excinfo.value)
