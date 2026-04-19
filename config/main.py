from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict, List
import uvicorn

app = FastAPI()

#{"service_name": ["ip1", "ip2"]}
registry: Dict[str, List[str]] = {}

@app.post("/register")
async def register(service_name: str, request: Request):
    client_host = request.client.host
    if service_name not in registry:
        registry[service_name] = []
    if client_host not in registry[service_name]:
        registry[service_name].append(client_host)
    return {"status": "registered", "ip": client_host}

@app.get("/nodes/{service_name}")
async def get_nodes(service_name: str):
    return registry.get(service_name, [])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)