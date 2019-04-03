from __future__ import print_function

import base64
import random
import string
import uuid

from kubernetes import client, config
from kubernetes.client.rest import ApiException


def create_secret(api_token_dir, accessing_kubernetes_api_url, namespace, metadata, data):
    """
    Creates secret of given data and metadata in given namespace
    :param api_token_dir: directory to your ApiToken
    :param accessing_kubernetes_api_url: url that provides access to kubernetes api
    :param namespace: namespace name where you create secret
    :param metadata: metadata that is contained a nested object field called 'metadata'
                    MUST have the following:
                    'namespace' a DNS compatible label that objects are subdivided into
                    'name' a string that uniquely identifies this object within the current namespace
                    'uid' a unique in time and space uuid value
    :param data: secret data encoded with base64
    """
    config.load_kube_config()

    configuration = client.Configuration()
    api_token = open(api_token_dir, mode='r').read()
    configuration.api_key["authorization"] = 'Bearer ' + api_token
    configuration.host = 'http://' + accessing_kubernetes_api_url
    configuration.verify_ssl = False
    api_instance = client.CoreV1Api(client.ApiClient(configuration))

    api_version = 'v1'
    kind = 'Secret'
    body = client.V1Secret(api_version, data, kind, metadata, type='kubernetes.io/tls')
    try:
        api_response = api_instance.create_namespaced_secret(namespace, body, pretty='true')
        print(api_response)
    except ApiException as e:
        print("Exception when calling CoreV1Api->create_namespaced_secret: %s\n" % e)
        return False


def random_string(size=6, chars=string.ascii_uppercase + string.digits):
    """
        Needed for making unique name field in metadata
        """
    return ''.join(random.choice(chars) for x in range(size))


# Example
namespace = 'test-namespace'
# 'name' must be unique in namespace
# 'namespace' must  be the same as namespace argument of a function
# 'uid' must be unique in  time and  space
metadata = {'name': random_string(8), 'namespace': namespace, 'uid': str(uuid.uuid4())}
# values must be encoded with base64
bytecode_crt = base64.b64encode(b'myValue')
bytecode_key = base64.b64encode(b'myKey')
data = {'tls.crt': bytecode_crt.decode('utf-8'), 'tls.key': bytecode_key.decode('utf-8')}

create_secret('api_token', '127.0.0.1:8080', 'test-namespace', metadata, data)
