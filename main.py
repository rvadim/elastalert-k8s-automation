import os
import time

from kubernetes import config
import logging
from config_generator import Renderer
from config_readers import LocalUserConfigReader
from config_readers import RemoteUserConfigReader
from config_readers import get_admin_config_file


logging.basicConfig(level=os.environ.get('LOG_LEVEL', logging.INFO))
log = logging.getLogger(__name__)


def main():
    local_run = os.environ.get('LOCAL_RUN') == '1'
    log.info(f'Local run: {local_run}')
    config_dir = os.environ.get('CONFIG_DIR', './eka/')
    log.info(f'CONFIG_DIR: {config_dir}')
    ea_config_path = os.environ.get('ELASTALERT_CONFIG_DIR', './config/')
    log.info(f'ELASTALERT_CONFIG_DIR: {ea_config_path}')
    context = get_admin_config_file(os.path.join(config_dir, 'config.yaml'))

    user_rules_directory = os.path.join(ea_config_path, 'rules')
    log.info(f'user_rules_directory: {user_rules_directory}')
    context['rules_folder'] = user_rules_directory

    renderer = Renderer(context, './templates')
    with open(os.path.join(ea_config_path, 'config.yaml'), 'w') as f:
        f.write(renderer.generate_ea_config())

    if local_run:
        reader = LocalUserConfigReader(os.path.join(config_dir, 'rules'))
    else:
        config.load_kube_config()
        reader = RemoteUserConfigReader()

    while True:
        if not os.path.exists(user_rules_directory):
            os.makedirs(user_rules_directory, 0o755)
        # Drop all files from user rules directory
        for f in os.listdir(user_rules_directory):
            f_path = os.path.join(user_rules_directory, f)
            os.remove(f_path)

        user_configs = reader.get_config_files()
        ea_rules = renderer.generate_ea_rules(user_configs)

        for i, rule in enumerate(ea_rules):
            with open(os.path.join(user_rules_directory, f'rule_{i}.yaml'), 'w') as output:
                output.write(rule)

        time.sleep(60)


if __name__ == "__main__":
    main()
