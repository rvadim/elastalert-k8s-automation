from kubernetes import config


def main():
    config.load_incluster_config()


if __name__ == "__main__":
    main()
