from config_generator import Renderer
import yaml


class TestJinjaCustomFilter:
    def test_yaml_filter(self):
        renderer = Renderer('./tests/fixtures/test_jinja')
        parsed_file = yaml.safe_load(open('./tests/fixtures/test_jinja/file_for_render'))
        generated = renderer._generate_config('test_yaml_filter_template.j2', parsed_file)
        assert parsed_file == yaml.safe_load(generated)
