from kubernetes import client
from kubernetes.client.rest import ApiException


def get_configmap_from_namespace(api_token_dir: str, accessing_kubernetes_api_url: str, namespace_name: str):
    """
    :param api_token_dir: directory to your ApiToken
        Note: to get ApiToken use bash command below:
    kubectl describe secret $(kubectl get secrets | grep default | cut -f1 -d ' ') \
    | grep -E '^token' | cut -f2 -d':' | tr -d '\t'
    :type api_token_dir: str
    :param accessing_kubernetes_api_url: url that provides access to kubernetes api
        Note: to access kubernetes api use command below
            kubectl proxy --port=8080
            result will be like: Starting to serve on 127.0.0.1:8080
    :type accessing_kubernetes_api_url: str
    :param namespace_name: namespace name that contains configmap
    :type namespace_name: str
    :return: True if response received successfully, False otherwise
    """
    configuration = client.Configuration()
    api_token = open(api_token_dir, mode='r').read()
    configuration.api_key["authorization"] = 'Bearer ' + api_token
    configuration.host = 'http://' + accessing_kubernetes_api_url
    configuration.verify_ssl = False
    api_instance = client.CoreV1Api(client.ApiClient(configuration))
    try:
        api_response = api_instance.list_namespaced_config_map(namespace_name,
                                                               pretty='true',
                                                               limit=56,
                                                               timeout_seconds=56)
        print(api_response)
        return True
    except ApiException as e:
        print("Exception when calling CoreV1Api->list_namespaced_config_map: %s\n" % e)
        return False


# Example
get_configmap_from_namespace('api_token', '127.0.0.1:8080', 'default')
