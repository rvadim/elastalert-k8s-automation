import config_readers
import os
from unittest.mock import Mock
from mock import patch


class TestReader:
    def test_local_reading_config(self):
        reader = config_readers.LocalUserConfigReader('./tests/fixtures/test_user_configs/')
        res = reader.get_config_files()
        assert len(res) == 2

    def test_remote_reading_config(self):
        test_file_path = './tests/fixtures/test_user_configs/'
        configmap_mock = Mock()
        configmap_mock.metadata.namespace = 'test_namespace'
        configmap_mock.metadata.name = 'test_configmap_name'
        configmap_data = dict()
        test_conf_num = 1
        for file in os.listdir(test_file_path):
            file_path = os.path.join(test_file_path, file)
            configmap_data['test_user_config ' + str(test_conf_num)] = open(file_path, 'r')
            test_conf_num += 1
        configmap_mock.data = configmap_data
        with patch('config_readers.RemoteUserConfigReader._get_configmap_list') \
                as get_configmap_list:
            get_configmap_list.return_value = [configmap_mock]
            cluster_config_dummy = Mock()
            config_reader = config_readers.RemoteUserConfigReader(cluster_config_dummy)
            assert len(config_reader.get_config_files()) == 2
