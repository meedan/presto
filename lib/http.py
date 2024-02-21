import json
import datetime
from typing import Any, Dict
import httpx
from httpx import HTTPStatusError
from fastapi import FastAPI, Request
from pydantic import BaseModel
from lib.queue.worker import QueueWorker
from lib.queue.queue import Queue
from lib.logger import logger
from lib import schemas
from lib.sentry import sentry_sdk
from lib.helpers import get_setting, get_environment_setting

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
    queue_prefix = Queue.get_queue_prefix()
    queue_suffix = Queue.get_queue_suffix()
    queue = QueueWorker.create(process_name)
    queue.push_message(f"{queue_prefix}{process_name}{queue_suffix}", schemas.Message(body=message, model_name=process_name))
    return {"message": "Message pushed successfully", "queue": process_name, "body": message}

@app.post("/trigger_callback")
async def trigger_callback(message: Dict[str, Any]):
    url = message.get("callback_url")
    if url:
      response = await post_url(url, message)
      if isinstance(response, dict) and response.get("error"):
          return response
      else:
          return {"message": "Message Called Back Successfully"}
    else:
      return {"message": "No Message Callback, Passing"}

@app.head("/ping")
def head_ping():
    return {"pong": 1}

@app.get("/ping")
def get_ping():
    return {"pong": 1}

@app.post("/echo")
async def echo(message: Dict[str, Any]):
    logger.info(f"About to echo message of {message}")
    return {"echo": message}