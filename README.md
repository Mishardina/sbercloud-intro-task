# sbercloud-intro-task
Intro task for interview in SberCloud

## Deployment
### locally
Prerequsites: MongoDB Docker image.
First, build the Docker image by the command
```
docker build -t bookapp-python .
```
Secondly, run the following commands:
```
docker network create tasksapp-net
docker run --name=mongo --rm -d --network=tasksapp-net mongo
docker run –-name=tasksapp-python --rm -p 5000:5000 -d –-network=tasksapp-net varunkumarg/tasksapp-python:1.0.0
```
### on k8s cluster
Run next commands to deploy on Kubernetes cluster:
```
kubectl create -f tasksapp.yaml
kubectl create -f tasksapp-svc.yaml
kubectl create -f mongo-pv.yaml
kubectl create -f mongo-pvc.yaml
kubectl create -f mongo.yaml
kubectl create -f mongo-svc.yaml
```
