# import datetime
# from lib.queue.queue import Queue
# queue = Queue.create("input", "output")
# queue.push_message(queue.input_queue, {"body": {"id": 1, "callback_url": "http://example.com", "text": "This is a test"}, "input_queue": queue.input_queue_name, "output_queue": queue.output_queue_name, "start_time": str(datetime.datetime.now())})
#
import json
import datetime
from typing import Any, Dict
import httpx
from httpx import HTTPStatusError
from fastapi import FastAPI, Request
from pydantic import BaseModel
from lib.queue.queue import Queue
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

@app.post("/fingerprint_item/{fingerprinter}")
def fingerprint_item(fingerprinter: str, message: Dict[str, Any]):
    queue = Queue.create(fingerprinter, f"{fingerprinter}-output")
    queue.push_message(queue.input_queue_name, schemas.Message(body=message, input_queue=queue.input_queue_name, output_queue=queue.output_queue_name, start_time=str(datetime.datetime.now())))
    return {"message": "Message pushed successfully"}

@app.post("/trigger_callback")
async def fingerprint_item(message: Dict[str, Any]):
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
def fingerprint_item():
    return {"pong": 1}
