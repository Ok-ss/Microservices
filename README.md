# Microservices
## Strtup:
```
cd Microservices
docker compose up --build -d
```
## Usage: 
To add to/substract form an account:
```
curl -X POST http://localhost:8000/send   -H "Content-Type: application/json"   -d '{"user_id":[your user_id], "amount":[+/- amount you wish to add/substract]}'
```
To see the balance and transactions of an account:
```
curl http://localhost:8000/user/[your user_id]
```
To see the balances of all users:
```
curl http://localhost:8000/accounts
```
## Additional:
Additional information is in the protocol.pdf file
