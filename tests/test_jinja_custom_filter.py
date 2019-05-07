from config_generator import yaml_filter
from jinja2 import Environment, FileSystemLoader
import yaml


class TestJinjaCustomFilter:
    def test_yaml_filter(self):
        env = Environment(loader=FileSystemLoader('./tests/fixtures/test_jinja'))
        env.filters['toyaml'] = yaml_filter
        template = env.get_template('test_yaml_filter_template.j2')
        parsed_file = yaml.safe_load(open('./tests/fixtures/test_jinja/file_for_render'))
        assert parsed_file == yaml.safe_load(template.render(parsed_file))
