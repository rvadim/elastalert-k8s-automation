import pytest

from config_generator import Renderer
from config_readers import get_admin_config_file, LocalUserConfigReader


class TestConfigGenerator:

    @pytest.fixture
    def renderer(self):
        context = get_admin_config_file('tests/fixtures/renderer_test_config.yaml')
        return Renderer(context, './templates')

    @pytest.fixture
    def required_options(self):
        required_options = {'email': ['smtp_host', 'smtp_port'],
                            'slack': ['slack_webhook_url']}
        return required_options

    @classmethod
    def contains_required_options(cls, config, options):
        for option in options:
            if option not in config:
                return False
        return True

    def test_example(self, renderer, required_options):
        reader = LocalUserConfigReader('tests/fixtures/renderer_test_user_rules')
        user_configs = reader.get_config_files()

        for conf in user_configs:
            renderer.add_alerts_options(conf)
            for alert in conf['alert']:
                if isinstance(alert, dict):
                    alert_type = list(alert.keys())[0]
                    config = alert[alert_type]
                else:
                    alert_type = alert
                    config = conf

                assert alert_type in required_options
                assert TestConfigGenerator.contains_required_options(config,
                                                                     required_options[alert_type])

                assert f'{alert_type}_id' not in config
