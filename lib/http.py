import httpx
import datetime
from fastapi import FastAPI
from typing import Any, Dict
from pydantic import BaseModel
from lib.queue.queue import Queue

app = FastAPI()
async def post_url(url: str, params: dict) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=json.dumps(params))
        response.raise_for_status()
        return response.json()

@app.post("/fingerprint_item/{fingerprinter}")
async def fingerprint_item(fingerprinter: str, message: Dict[str, Any]):
    queue = await Queue.create(fingerprinter, f"{fingerprinter}-output")
    queue.push_message(queue.input_queue_name, {"body": message, "input_queue": queue.input_queue_name, "output_queue": queue.output_queue_name, "start_time": str(datetime.datetime.now())})
    return {"message": "Message pushed successfully"}

@app.post("/trigger_callback")
async def fingerprint_item(message: Dict[str, Any]):
    url = message.get("callback_url")
    if url:
      response = await post_url(url, message)
      return {"message": "Message Called Back Successfully"}
    else:
      return {"message": "No Message Callback, Passing"}


