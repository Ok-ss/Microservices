# Microservices
## Setup:
```
source ./Microservices/bin/activate
docker compose build --no-cache
```
## Run:
```
docker compose up --scale logging=3 --scale hazelcast=3 -d
```
