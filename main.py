import os

from fastapi import FastAPI, Depends, Security, HTTPException
from app.router.routes import router
from dotenv import load_dotenv
from fastapi.security.api_key import APIKeyHeader, APIKey
from fastapi.middleware.cors import CORSMiddleware
from app.service.RabbitService import RabbitMQService
import threading

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key_header = APIKeyHeader(name=os.getenv('FAST_API_KEY_NAME'), auto_error=True)


async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == os.getenv('FAST_API_ACCESS_TOKEN'):
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


app.include_router(router, dependencies=[Depends(get_api_key)])

# This is a comment
@app.on_event("startup")
async def startup_event():
    # Start the RabbitMQ consumer in a separate thread
    rabbitmqService = RabbitMQService()
    thread = threading.Thread(target=rabbitmqService.start_consuming)
    thread.daemon = True
    thread.start()