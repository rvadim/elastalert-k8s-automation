from jinja2 import Environment, FileSystemLoader
from config import get_env_vars_by_prefix


def get_env(templates_dir):
    return Environment(loader=FileSystemLoader(templates_dir))


class Renderer:
    """
    Class for rendering ElastAlert configurations
    """
    def __init__(self, templates_dir='./templates'):
        self.templates_dir = templates_dir
        self.env = get_env(self.templates_dir)

    def _generate_config(self, template_name, context):
        template = self.env.get_template(template_name)
        return template.render(context)

    def generate_ea_config(self, adm_context):
        return self._generate_config('ea_config.yaml.j2', adm_context)

    def generate_ea_rules(self, user_configs):
        ea_rules = []
        for conf in user_configs:
            rule_context = dict(conf)
            rule_context.update(get_env_vars_by_prefix())
            ea_rules.append(self._generate_config('ea_rule.yaml.j2', rule_context))
        return ea_rules
