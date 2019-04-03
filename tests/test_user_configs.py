from copy import copy
import yaml

from config import validate_user_rule


class TestUserConfig:
    required_properties = ['index', 'type']
    properties_types = [str, str]

    @classmethod
    def build_test_config(cls):
        test_config = {}
        test_config['es_host'] = '127.0.0.1'
        test_config['es_port'] = 80
        test_config['index'] = 'test_index'
        test_config['type'] = 'any'

        return test_config

    def test_correct_config(self):
        user_rule = TestUserConfig.build_test_config()
        errors = list(validate_user_rule(user_rule))
        assert len(errors) == 0

    def test_missing_required_property(self):
        test_config = self.build_test_config()

        for p in TestUserConfig.required_properties:
            current_config = copy(test_config)
            del current_config[p]
            current_config = yaml.dump(current_config)

            user_rule = yaml.safe_load(current_config)
            errors = list(validate_user_rule(user_rule))
            assert len(errors) == 1
            assert f'{p} in configuration file is None, please specify {p}' in str(errors[0])

    def test_incorrect_property_type(self):
        test_config = self.build_test_config()

        for p, t in zip(TestUserConfig.required_properties, TestUserConfig.properties_types):
            current_config = copy(test_config)
            current_config[p] = 0.1
            current_config = yaml.dump(current_config)

            user_rule = yaml.safe_load(current_config)
            errors = list(validate_user_rule(user_rule))
            assert len(errors) == 1
            assert f'{p} in configuration file is not {t}, type: {type(0.1)}' in str(errors[0])

    def test_rule_type(self):
        correct_types = {'any', 'blacklist', 'whitelist', 'change', 'frequency', 'spike',
                         'flatline', 'new_term', 'cardinality', 'metric_aggregation', 'percentage_match'}
        test_config = self.build_test_config()

        for t in correct_types:
            current_config = copy(test_config)
            current_config['type'] = t
            current_config = yaml.dump(current_config)

            user_rule = yaml.safe_load(current_config)
            errors = list(validate_user_rule(user_rule))
            assert len(errors) == 0

        test_config['type'] = 'incorrect_type'
        test_config = yaml.dump(test_config)

        user_rule = yaml.safe_load(test_config)
        errors = list(validate_user_rule(user_rule))
        assert len(errors) == 1
        assert f'Elastalert rule type incorrect_type in configuration is incorrect.' in str(errors[0])
