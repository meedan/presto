# from lib import schemas
# from lib.queue.worker import QueueWorker
# queue = QueueWorker.create("audio__Model")
# queue.push_message("audio__Model", schemas.Message(body={'callback_url': 'http://alegre:3100/presto/receive/add_item/audio', 'id': 123, 'url':'http://devingaffney.com/files/blah.mp3', 'text': None, 'raw': {'doc_id': 123, 'url': 'http://devingaffney.com/files/blah.mp3'}}))
import json
import datetime
from typing import Any, Dict
import httpx
from httpx import HTTPStatusError
from fastapi import FastAPI, Request
from pydantic import BaseModel
from lib.queue.worker import QueueWorker
from lib.logger import logger
from lib import schemas

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Calling endpoint: {request.url.path}")
    response = await call_next(request)
    logger.info(f"Endpoint {request.url.path} returned: {response.status_code}")
    return response

async def post_url(url: str, params: dict) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, data=json.dumps(params))
            response.raise_for_status()
            return response.json()
        except HTTPStatusError:
            return {"error": f"HTTP Error on Attempt to call {url} with {params}"}

@app.post("/process_item/{process_name}")
def process_item(process_name: str, message: Dict[str, Any]):
    logger.info(message)
    queue = QueueWorker.create(process_name)
    queue.push_message(process_name, schemas.Message(body=message))
    return {"message": "Message pushed successfully", "queue": process_name, "body": message}

@app.post("/trigger_callback")
async def process_item(message: Dict[str, Any]):
    url = message.get("callback_url")
    if url:
      response = await post_url(url, message)
      if isinstance(response, dict) and response.get("error"):
          return response
      else:
          return {"message": "Message Called Back Successfully"}
    else:
      return {"message": "No Message Callback, Passing"}

@app.get("/ping")
def process_item():
    return {"pong": 1}

@app.post("/echo")
async def echo(message: Dict[str, Any]):
    logger.info(f"About to echo message of {message}")
    return {"echo": message}