import json
import datetime
from typing import Any, Dict
import httpx
from httpx import HTTPStatusError
from fastapi import FastAPI
from pydantic import BaseModel
from lib.queue.queue import Queue

app = FastAPI()
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
    queue.push_message(queue.input_queue_name, {"body": message, "input_queue": queue.input_queue_name, "output_queue": queue.output_queue_name, "start_time": str(datetime.datetime.now())})
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


