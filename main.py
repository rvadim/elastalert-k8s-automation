import os
import sys
from config import parse_config
from config import validate
from kubernetes import config

import logging
logging.basicConfig(level=os.environ.get('LOG_LEVEL', logging.INFO))
log = logging.getLogger(__name__)


def main():
    config_path = os.environ.get('CONFIG', 'config.yaml')
    log.info('Reading configuration file "{}"...', config_path)
    errors = validate(parse_config(config_path))
    if len(errors) != 0:
        for error in errors:
            log.error(error)
        sys.exit(1)
    config.load_incluster_config()


if __name__ == "__main__":
    main()
