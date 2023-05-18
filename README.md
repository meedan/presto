## PRESTO

Presto is a Python service that aims to perform, most generally, on-demand media fingerprints at scale. In the context of text, fingerprints are transformer vectors - video is done by TMK, images by PDQ, and audio by chromaprint.

Presto performs text vectorization using different Hugging Face models. The texts are enqueued via a generic Queue class, which can either be a Redis (local) or SQS (production) instance. The project's directory structure consists of two main directories, `model/` and `queue/`, which contain classes for different models and queues, respectively. The `test/` directory contains test classes for the different models and queues. Audio, Image, and Video fingerprinting are accomplished by specific packages aimed at those tasks. Text generates lists of floats as output (i.e. vectors), while Audio, Image, And Video generate string represented bitfields or hashes. Video additionally generates .tmk files which are ≈250kb files typically (though the file can technically grow as the video length grows).

### Dependencies

This project requires the following dependencies, which are listed in the `requirements.txt` file:
- boto3==1.18.64
- pyacoustid==1.2.2
- redis==4.4.4
- sentence-transformers==2.2.0
- tmkpy==0.1.1
- torch==1.9.0
- transformers==4.6.0


Depending on your environment, and if you are using Docker directly or not, these dependencies may force you install other development packages.

### Architectural Diagrams

![Architecture Diagram](img/presto_architectural_diagram.png?raw=true "Architecture Diagram")

![Architecture Flowchart](img/presto_flowchart.png?raw=true "Architecture Flowchart")


### Setup
To run the project, you can use the provided `Dockerfile`, or start via `docker-compose build && docker-compose up`. This file sets up the environment by installing the required dependencies and running the `run.py` file when the container is started. To build and run the Docker image from the Dockerfile directly, run the following commands:

```
docker build -t text-vectorization .
docker run -e QUEUE_TYPE=<queue_type> -e INPUT_QUEUE_NAME=<input_queue_name> -e OUTPUT_QUEUE_NAME=<output_queue_name> -e MODEL_NAME=<model_name> 
```

Here, we require at least three environment variables - `queue_type`, `input_queue_name`, and `model_name`. If left unspecified, `output_queue_name` will be automatically set to `input_queue_name[-output]`. Depending on your usage, you may need to replace `<queue_type>`, `<input_queue_name>`, `<output_queue_name>`, and `<model_name>` with the appropriate values.

Currently supported `model_name` values are just module names keyed from the `model` directory, and currently are as follows:

* `fptg.MdebertaFilipino` - text model, uses `meedan/paraphrase-filipino-mpnet-base-v2`
* `indian_sbert.IndianSbert` - text model, uses `meedan/indian-sbert`
* `mean_tokens.XlmRBertBaseNliStsbMeanTokens` - text model, uses `xlm-r-bert-base-nli-stsb-mean-tokens`
* `video.VideoModel` - video model
* `image.ImageModel` - image model
* `audio.AudioModel` - audio model

### Makefile
The Makefile contains two targets, `run` and `run_test`. `run` runs the `run.py` file when executed. Remember to have the environment variables described above defined. `run_test` runs the test suite which is expected to be passing currently - reach out if it fails on your hardware!

### run.py
The `run.py` file is the main routine that runs the vectorization process. It sets up the queue and model instances, receives messages from the queue, applies the model to the messages, responds to the queue with the vectorized text, and deletes the original messages in a loop within the `queue.process_messages` function. The `os.environ` statements retrieve environment variables to create the queue and model instances.

### Queues

Presto is able to `process_messages` via redis or SQS. In practice, we use redis for local development, and SQS for production environments. When interacting with a `queue`, we use the generic superclass `queue`. `queue.fingerprint` takes as an argument a `model` instance. The `fingerprint` routine collects a batch of `BATCH_SIZE` messages appropriate to the `BATCH_SIZE` for the `model` specified. Once pulled from the `input_queue`, those messages are processed via `model.respond`. The resulting fingerprint outputs from the model are then zipped with the original message pulled from the `input_queue`, and a message is placed onto the `output_queue` that consists of exactly: `{"request": message, "response": response}`.

### Models

Models are defined by inheriting from the `lib.model.model.Model` superclass - all models require a `respond` function which accepts one or more `messages` which are individual items popped from whatever `queue` is currently in use. The number of messages a `model` can consume concurrently is specified by the `BATCH_SIZE` variable - if not explicitly set within the model, it defaults to 1 (i.e. single-threaded). It is the responsibility of anyone writing a new model to pack in whatever metadata is useful to transmit across the queue response into the return value of the `respond` function - including returning the individual original messages (eventually we'll abstract that requirement out, but not today).

### Messages

Messages passed to presto input queues must have the following structure, per each model type:

#### Text
Input Message:
```
{
  "callback_url": "A unique URL that will be requested upon completion",
  "text": "The text to be processed by the vectorizer"
}
```
Output Message:
```
{
  "callback_url": "A unique URL that will be requested upon completion",
  "text": "The text to be processed by the vectorizer",
  "response": [List of floats representing vectorization results],
}
```

#### Video
Input Message:
```
{
  "callback_url": "A unique URL that will be requested upon completion",
  "url": "The URL at which the media is located",
}
```
Output Message:
```
{
  "callback_url": "A unique URL that will be requested upon completion",
  "url": "The URL at which the media is located",
  "bucket": "bucket within which the .tmk file is stored",
  "outfile": "The filename of the .tmk file generated for the video",
  "hash_value": "The shorter, getPureAverageFeature hash from tmk (used in first-pass approximation searches)",
}
```

#### Audio
Input Message:
```
{
  "callback_url": "A unique URL that will be requested upon completion",
  "url": "The URL at which the media is located"
}
```
Output Message:
```
{
  "callback_url": "A unique URL that will be requested upon completion",
  "url": "The URL at which the media is located",
  "hash_value": [pyacoustid output hash value for the audio clip],
}
```


#### Image
Input Message:
```
{
  "callback_url": "A unique URL that will be requested upon completion",
  "url": "The URL at which the media is located",
}
```
Output Message:
```
{
  "callback_url": "A unique URL that will be requested upon completion",
  "url": "The URL at which the media is located",
  "hash_value": [pdqhasher output hash value for the image],
}
```
