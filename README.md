# Microservices with Kubernetes
## Setup
```minikube start
eval $(minikube docker-env)
docker build -t microservices-logging ./logging
docker build -t microservices-counter ./counter
docker build -t microservices-facade ./facade
kubectl apply -f k8s-manifests/
kubectl rollout restart deployment postgres
kubectl rollout restart deployment hazelcast
kubectl rollout restart deployment logging-service
kubectl rollout restart deployment counter-service
kubectl rollout restart deployment facade-service
```
## Service-managing Commands:
```
kubectl scale deployment &lt;service-name&gt; --replicas=&lt;number of replicas&gt;       #scales the service up or down
kubectl get pods                                                                          #allows to see all pods with statuses
kubectl delete pod &lt;full pod name&gt;                                                  #delete a pod and get a new one
minikube service facade-service --url                                                     #get a service IP and port
```
## Comands to a service:
```
curl -X POST http://&lt;Service IP and port&gt;/send\                                     # add or substract money from the user_id account
      -H "Content-Type: application/json"\
      -d '{"user_id": &lt;user_id&gt;, "amount": &lt;amount&gt;}                          
curl http://&lt;Service IP and port&gt;/user/&lt;user_id&gt;                              #get user_id balance and transactions
curl http://&lt;Service IP and port&gt;/accounts                                          #get all balances

```
