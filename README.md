# elastalert-k8s-automation
Use power of Kubernetes to automation configuration of elastaler

## Building
To build and upload image to the repository run the following commands:
```
docker-compose build
docker-compose push
```

## Running
For running project in minikube start a cluster by:
```
minikube start
```
Then you can run:
```
kubectl apply -f deploy/deploy.yaml
```

## General alert settings
The administrator can set the general system settings for the alerts in the admin config. This settings will be used by users in their rules. This allows users not to specify general settings in each rule. In addition, this ensures that all secret information (authorization data, keys, etc.) will be stored only by the administrator, and end users will not need to have access to it.

The alert settings in the admin config have the following structure:

```yaml
alert_configs:
 email:
   default: mail_id_1
   configs:
     mail_id_1:
       # Email ElastAlert settings for mail_id_1
     mail_id_2:
       # Email ElastAlert settings for mail_id_2
     ...
 slack:
   default: slack_id_1
   configs:
     slack_id_1:
        # Slack ElastAlert settings for slack_id_1
     ...
 ...

```

All settings are specified by the “alert_configs” option in the admin config. For each type of alerts that will be used in the system, the administrator must specify a list of configurations (the “configs” option) and a default configuration (the “default” option). The settings for each individual configuration are specified in ElastAlert format, more detailed information can be found in the documentation:

https://elastalert.readthedocs.io/en/latest/ruletypes.html#alerts

Example of general alert settings in the admin config can be found in

/tests/fixtures/renderer_test_config.yaml


## User rules
User rules should be set in the configmap named “elastalert-rules”. Each such configmap must contain a set of named rules.

Rules are created in the format of ElastAlert user rules and can contain any valid ElastAlert options.

In addition, for alerts there is a special option {alert}_id (where {alert} is the type of alert supported by ElastAlert, for example, email). {alert}_id determines which system settings specified by the administrator will be used for this alert. If {alert}_id is not specified or refers to a nonexistent system settings, the default settings will be used.
Examples of user rules can be found in

/tests/fixtures/renderer_test_user_rules

For more information on user rules for ElastAlert, see the documentation:

https://elastalert.readthedocs.io/en/latest/ruletypes.html


