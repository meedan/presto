import time
import os
import importlib
import copy
from lib.queue.queue import Queue
from lib.model.model import Model
batch_map = {
    "indian_sbert.IndianSbert": 100,
    "mean_tokens.XlmRBertBaseNliStsbMeanTokens": 100,
    "fptg.MdebertaFilipino": 100,
    "video.VideoModel": 1,
    "audio.AudioModel": 1
}
queue = Queue.create(
    os.environ.get('QUEUE_TYPE'),
    os.environ.get('INPUT_QUEUE_NAME')+"2",
    os.environ.get('OUTPUT_QUEUE_NAME'),
    batch_map.get(os.environ.get('MODEL_NAME'), 10)
)

model = Model.create(
    os.environ.get('MODEL_NAME')
)

while True:
    time.sleep(1)

while True:
    messages = queue.receive_messages()
    responses = model.respond(copy.deepcopy(messages))
    for message, response in zip(messages, responses):
        queue.respond(response)
        queue.delete_message(message)
