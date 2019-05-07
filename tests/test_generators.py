import yaml
from config_readers import LocalUserConfigReader
from config_generator import Renderer


class TestGen:
    def test_created_as_yaml(self):
        reader = LocalUserConfigReader('./tests/fixtures/test_user_configs/')
        user_configs = reader.get_config_files()
        generated_rules = Renderer('./templates').generate_ea_rules(user_configs)
        err_list = []
        for gen_rule in generated_rules:
            try:
                yaml.safe_load(gen_rule)
            except Exception as e:
                err_list.append(e)
        assert len(err_list) == 0
