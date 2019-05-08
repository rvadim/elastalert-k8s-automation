# elastalert-k8s-automation
Use power of Kubernetes to automation configuration of ElastAlert.

The goal of the current project is to simplify configuring ElastAlert notifications about events of some other 
applications that store its logs in ElasticSearch.

There are two modes for running this application: the local mode and the remote mode.
* Remote mode is intended for running application in Kubernetes cluster where ElastAlert 
is started.
* Local mode allows to run application without deployment in Kubernetes. 

The application uses two types of configuration files to configure work of ElastAlert:
* Administrator configuration file with general properties and notification options.
* User rules configuration files that determine rules for ElastAlert.

The application collects both types of configuration files and generates configuration for ElastAlert.

##Installing and configuring
Clone elastlert-k8s-automation project:
````
$ git clone https://github.com/rvadim/elastalert-k8s-automation.git
````

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

rules_folder: # Directory with ElastAlert rules

run_every: # Frequency of queries to ElasticSearch
  
buffer_time: # Size of the query window, stretching backwards from the time each query is run. 
            #This value is ignored for rules where use_count_query or use_terms_query is set to true.

writeback_index: # ElasticSearch index for ElastAlert logs 
```

Example of administrator configuration file can be found in 

/tests/fixtures/valid_config.yaml

More information about configuring ElastAlert, can be found in official documentation:

https://elastalert.readthedocs.io/en/latest/running_elastalert.html

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

Example of general alert settings in the admin config can be found in

/tests/fixtures/renderer_test_config.yaml

### User rules configuration files
User rules should be set in the configmap named “elastalert-rules”. Each such configmap must contain a set of named rules.

Rules are created in the format of ElastAlert user rules and can contain any valid ElastAlert options.

In addition, for alerts there is a special option {alert}_id (where {alert} is the type of alert supported by ElastAlert, 
for example, email). {alert}_id determines which system settings specified by the administrator will be used for this 
alert. If {alert}_id is not specified or refers to a nonexistent system settings, the default settings will be used.
Examples of user rules can be found in

/tests/fixtures/renderer_test_user_rules.yaml

For more information on user rules for ElastAlert, see the documentation:

https://elastalert.readthedocs.io/en/latest/ruletypes.html

##Running the application
###Local run 
###Remote run
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
