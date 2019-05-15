# elastalert-k8s-automation
Use power of Kubernetes to automation configuration of ElastAlert.

The goal of the current project is to simplify configuring ElastAlert notifications about events of some other 
applications that store its logs in ElasticSearch.

There are two modes for running this application: the local mode and the remote mode.
* Remote mode is intended for running application in Kubernetes cluster where ElastAlert 
is started.
* Local mode allows to run application without deployment in Kubernetes. It was created for testing purposes.

The application uses two types of configuration files to configure work of ElastAlert:
* Administrator configuration file with general properties and notification options.
* User rules configuration files that determine rules for ElastAlert.

The application collects both types of configuration files and generates configuration for ElastAlert.

## Installing and configuring
* To run application remotely, you have to download deployment file by executing the command
<br/><br/>
``
$ wget https://github.com/rvadim/elastalert-k8s-automation/raw/master/deploy/deploy.yaml
``
<br/><br/>
Then replace the data in the last section of the file with your administrator configuration file.
And install docker image in Kubernetes:
<br/><br/>
``
$ kubectl apply -f <path to file with deployment and config>
``
<br/><br/>
* To run application locally, clone elastlert-k8s-automation project:
<br/><br/>
``
$ git clone https://github.com/rvadim/elastalert-k8s-automation.git
``
<br/><br/>
And run `main.py` file after configuring application.  

Application can be configured by setting some environment variables:
* `LOCAL_RUN`: if specified by value `1`, the Local mode will be chosen. 
Otherwise the Remote mode wiil be chosen by default. (Optional)
* `CONFIG_DIR`: if specified, the directory to administrator configuration of this application will be 
specified by value of this variable. 
Otherwise configuration file will be taken from "./eka/" directory of this project. (Optional)
* `ELASTALERT_CONFIG_DIR`: if specified, the directory where generated ElastAlert configuration file will be placed. 
Otherwise generated ElastAlert configuration file will be placed in "./config/" directory of this project. (Optional)

*Note: it is assumed that ElastAlert and ElasticSearch are started*

### Administrator configuration file
The administrator configuration file must contain main options for ElastAlert and must have following structure:
```yaml
es_host: # Address of an ElasticSearch cluster
es_port: # Port for es_host

buffer_time: # Size of the query window, stretching backwards from the time each query is run. 
            #This value is ignored for rules where use_count_query or use_terms_query is set to true.

writeback_index: # ElasticSearch index for ElastAlert logs

run_every: # Frequency of queries to ElasticSearch

alert_configs:
    ...
    
# Optional properties
```

All the properties listed in this administrator configuration template are necessary for 
running ElastAlert. These properties have the same name and meaning as ElastAlert properties themselves (except `alert_configs`).  

More information about these and optional properties for configuring ElastAlert, can be found in official documentation:

https://elastalert.readthedocs.io/en/latest/running_elastalert.html

`alert_configs` section is described below.

Example of administrator configuration file can be found 
[here](https://github.com/rvadim/elastalert-k8s-automation/blob/master/examples/admin_config_example.yaml). 

*Note: ElastAlert properties such as passwords and alerter tokens are not expected to be set in configuration files 
due to sequrity issues. This data is supposed to be taken from application environment.*


#### General alert settings
The administrator can set the general system settings for the alerts in the admin config. This settings will be used 
by users in their rules. This allows users not to specify general settings in each rule. In addition, this ensures 
that all secret information (authorization data, keys, etc.) will be stored only by the administrator, and end users 
will not need to have access to it.

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

All settings are specified by the “alert_configs” option in the admin config. For each type of alerts that will be used 
in the system, the administrator must specify a list of configurations (the “configs” option) and a default configuration 
(the “default” option). The settings for each individual configuration are specified in ElastAlert format, more detailed 
information can be found in the documentation:

https://elastalert.readthedocs.io/en/latest/ruletypes.html#alerts

Example of general alert settings in the admin config:

```yaml
... # Other admin config options

alert_configs:
  email:
    default: mail_1
    configs:
      mail_1:
        smtp_host: localhost
        smtp_port: 25
      mail_2:
        smtp_host: localhost
        smtp_port: 27
  slack:
    default: slack_1
    configs:
      slack_1:
        slack_webhook_url: https://XXXXX.slack.com/services/new/incoming-webhook

```

### User rules configuration files
User rules should be set in the configmap named “elastalert-rules”. Each such configmap must contain a set of named rules.

Rules are created in the format of ElastAlert user rules and can contain any valid ElastAlert options.

In addition, for alerts there is a special option {alert}_id (where {alert} is the type of alert supported by ElastAlert, 
for example, email). {alert}_id determines which system settings specified by the administrator will be used for this 
alert. If {alert}_id is not specified or refers to a nonexistent system settings, the default settings will be used.
Example of user rule:


```yaml
index: example_index
type: any

alert:
  - email:
      email: example@gmail.com
      email_id: mail_1
  - email:
      email: example2@gmail.com
      email_id: mail_2
  - email:
      email: example3@gmail.com
      email_id: default         # In this case the default settings will be used
  - slack:
      slack_username_override: some_user
      slack_channel_override: some_channel
      slack_id: slack_1
  - slack:
      slack_username_override: another_user
      slack_channel_override: another_channel
      slack_id: incorrect_id    # If the {alert}_id is incorrect, the default settings will be used
```

For more information on user rules for ElastAlert, see the documentation:

https://elastalert.readthedocs.io/en/latest/ruletypes.html

## Running the application

### Local run 

### Remote run
To run elastlert-k8s-automation remotely, it is needed to be deployed in Kubernetes cluster.<br/>
To do that build and upload image of elastlert-k8s-automation to the repository by executing the following commands:
```
docker-compose build
docker-compose push
```
Start minikube cluster:
```
minikube start
```
And then you can run application:
```
kubectl apply -f deploy/deploy.yaml
```
