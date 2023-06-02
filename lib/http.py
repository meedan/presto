import datetime
from fastapi import FastAPI
from typing import Any, Dict
from pydantic import BaseModel
from queue.queue import Queue

app = FastAPI()

@app.post("/fingerprint_item/{fingerprinter}")
async def fingerprint_item(fingerprinter: str, message: Dict[str, Any]):
    queue = await Queue.create(fingerprinter, f"{fingerprinter}-output")
    queue.push_message(queue.input_queue_name, {"body": message, "input_queue": queue.input_queue_name, "output_queue": queue.output_queue_name, "start_time": str(datetime.datetime.now())})
    return {"message": "Message pushed successfully"}
