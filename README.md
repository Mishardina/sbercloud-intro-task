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
docker network create bookapp-net
docker run --name=mongo --rm -d --network=bookapp-net mongo
docker run –-name=bookapp-python --rm -p 5000:5000 -d –-network=bookapp-net bookapp-python
```
### on k8s cluster
Run next commands to deploy on Kubernetes cluster:
```
kubectl create -f bookapp.yaml
kubectl create -f bookapp-svc.yaml
kubectl create -f mongo-pv.yaml
kubectl create -f mongo-pvc.yaml
kubectl create -f mongo.yaml
kubectl create -f mongo-svc.yaml
```
