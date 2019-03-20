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
kubectl apply -f deploy.yaml
```
