import os
import time

from kubernetes import config
import logging
from generate_configs import Renderer
from readers import LocalUsrConfigReader
from readers import RemoteUsrConfigReader
from readers import get_admin_config_file


logging.basicConfig(level=os.environ.get('LOG_LEVEL', logging.INFO))
log = logging.getLogger(__name__)


def main():
    local_run = os.environ.get('LOCAL_RUN') == '1'
    config_dir = os.environ.get('CONFIG_DIR', './eka/')
    ea_config_path = os.environ.get('ELASTALERT_CONFIG_DIR', './config/')
    context = get_admin_config_file(os.path.join(config_dir, 'config.yaml'))

    user_rules_directory = os.path.join(ea_config_path, 'rules')
    context['rules_folder'] = user_rules_directory

    renderer = Renderer('./templates')
    with open(os.path.join(ea_config_path, 'config.yaml'), 'w') as f:
        f.write(renderer.generate_ea_config(context))

    if local_run:
        reader = LocalUsrConfigReader(os.path.join(config_dir, 'rules'))
    else:
        reader = RemoteUsrConfigReader(config.load_incluster_config())

    while True:
        if not os.path.exists(user_rules_directory):
            os.makedirs(user_rules_directory, 755)
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
