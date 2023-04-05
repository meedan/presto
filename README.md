## PRESTO

Presto is a Python service that aims to perform, most generally, on-demand media fingerprints at scale. In the context of text, fingerprints are transformer vectors - video is done by TMK, images by PDQ, and audio by chromaprint. Current, we only support text.

Presto performs text vectorization using different Hugging Face models. The texts are enqueued via a generic Queue class, which can either be a Redis (local) or SQS (production) instance. The project's directory structure consists of two main directories, `model/` and `queue/`, which contain classes for different models and queues, respectively. The `test/` directory contains test classes for the different models and queues.

### Dependencies

This project requires the following dependencies, which are listed in the `requirements.txt` file:
- boto3==1.18.64
- redis==3.5.3
- sentence-transformers==2.2.0
- torch==1.9.0
- transformers==4.10.2

Depending on your environment, and if you are using Docker directly or not, these dependencies may force you install other development packages.


### Setup
To run the project, you can use the provided `Dockerfile`, or start via `docker-compose build && docker-compose up`. This file sets up the environment by installing the required dependencies and running the `run.py` file when the container is started. To build and run the Docker image from the Dockerfile directly, run the following commands:

docker build -t text-vectorization .
docker run -e QUEUE_TYPE=<queue_type> -e INPUT_QUEUE_NAME=<input_queue_name> -e OUTPUT_QUEUE_NAME=<output_queue_name> -e MODEL_NAME=<model_name> 

Here, we require at least three environment variables - `queue_type`, `input_queue_name`, and `model_name`. If left unspecified, `output_queue_name` will be automatically set to `input_queue_name[-output]`. Depending on your usage, you may need to replace `<queue_type>`, `<input_queue_name>`, `<output_queue_name>`, and `<model_name>` with the appropriate values.

Currently supported `model_name` values are:

* `fptg` - uses `meedan/paraphrase-filipino-mpnet-base-v2`
* `indian_sbert` - uses `meedan/indian-sbert`
* `meantokens` - uses `xlm-r-bert-base-nli-stsb-mean-tokens`

### Makefile
The Makefile contains a single target, `run`, which runs the `run.py` file when executed. Remember to have the environment variables described above defined.

### run.py
The `run.py` file is the main routine that runs the vectorization process. It sets up the queue and model instances, receives messages from the queue, applies the model to the messages, responds to the queue with the vectorized text, and deletes the original messages. The `os.environ` statements retrieve environment variables to create the queue and model instances. The `batch_map` dictionary maps each model to its corresponding batch size.