from jinja2 import Environment, FileSystemLoader
from config import get_env_vars_by_prefix
import yaml


def get_env(templates_dir):
    return Environment(loader=FileSystemLoader(templates_dir))


def yaml_filter(dict_val):
    return yaml.dump(dict_val, default_flow_style=False)


class Renderer:
    """
    Class for rendering ElastAlert configurations
    """
    def __init__(self, admin_context, templates_dir='./templates'):
        self.templates_dir = templates_dir
        self.env = get_env(self.templates_dir)
        self.admin_context = admin_context
        self.env.filters['toyaml'] = yaml_filter

    def _generate_config(self, template_name, context):
        template = self.env.get_template(template_name)
        return template.render(context)

    def generate_ea_config(self):
        return self._generate_config('ea_config.yaml.j2', self.admin_context)

    def add_alerts_options(self, user_rule):
        alerts = user_rule['alert']
        for alert in alerts:
            if isinstance(alert, dict):
                alert_type = list(alert.keys())[0]
                alert_options = alert[alert_type]
            else:
                alert_type = alert
                alert_options = user_rule

            if alert_type not in self.admin_context['alert_configs']:
                continue

            config_name = alert_options[f'{alert_type}_id']
            alert_type_options = self.admin_context['alert_configs'][alert_type]

            if config_name not in alert_type_options \
                    or config_name == 'default':
                config_name = alert_type_options['default']

            alert_config = alert_type_options['configs'][config_name]
            alert_options.update(alert_config)
            del alert_options[f'{alert_type}_id']

    def generate_ea_rules(self, user_configs):
        ea_rules = []
        for conf in user_configs:
            self.add_alerts_options(conf)
            rule_context = dict(conf)
            rule_context.update(get_env_vars_by_prefix())
            ea_rules.append(self._generate_config('ea_rule.yaml.j2', rule_context))
        return ea_rules
