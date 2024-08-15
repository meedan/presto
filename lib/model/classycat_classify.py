from typing import Dict, Any
import os
import json
import uuid
import httpx
from openai import OpenAI
from anthropic import Anthropic
from lib.logger import logger
from lib.model.model import Model
from lib.schemas import Message, ClassyCatBatchClassificationResponse
from lib.s3 import load_file_from_s3, file_exists_in_s3, upload_file_to_s3
from lib.base_exception import PrestoBaseException


class LLMClient:
    def __init__(self):
        self.client = None

    def get_client(self):
        pass

    def classify(self, task_prompt, items_count, max_tokens_per_item=200):
        pass

class AnthropicClient(LLMClient):
    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name

    def get_client(self):
        if self.client is None:
            self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'), timeout=httpx.Timeout(60.0, read=60.0, write=60.0, connect=60.0), max_retries=0)
        return self.client

    def classify(self, task_prompt, items_count, max_tokens_per_item=200):
        client = self.get_client()
        completion = client.messages.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": task_prompt}
            ],
            max_tokens=(max_tokens_per_item * items_count) + 15,
            temperature=0.5
        )

        return completion.content[0].text

class OpenRouterClient(LLMClient):
    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name

    def get_client(self):
        if self.client is None:
            self.client = OpenAI(base_url='https://openrouter.ai/api/v1',
                                 api_key=os.environ.get('OPENROUTER_API_KEY'),
                                 timeout=httpx.Timeout(60.0, read=60.0, write=60.0, connect=60.0), max_retries=0)
        return self.client

    def classify(self, task_prompt, items_count, max_tokens_per_item=200):
        client = self.get_client()
        completion = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": task_prompt}
            ],
            max_tokens=(max_tokens_per_item * items_count) + 15,
            temperature=0.5
        )

        # TODO: record metric here with model name and number of items submitted (https://meedan.atlassian.net/browse/CV2-4987)

        return completion.choices[0].message.content


class Model(Model):
    def __init__(self):
        super().__init__()
        self.output_bucket = os.getenv("CLASSYCAT_OUTPUT_BUCKET")
        self.batch_size_limit = int(os.environ.get("CLASSYCAT_BATCH_SIZE_LIMIT"))
        llm_client_type = os.environ.get('CLASSYCAT_LLM_CLIENT_TYPE')
        llm_model_name = os.environ.get('CLASSYCAT_LLM_MODEL_NAME')
        self.llm_client = self.get_llm_client(llm_client_type, llm_model_name)

    def get_llm_client(self, client_type, model_name):
        if client_type == 'anthropic':
            return AnthropicClient(model_name)
        elif client_type == 'openrouter':
            return OpenRouterClient(model_name)
        else:
            raise PrestoBaseException(f"Unknown LLM client type {client_type}", 500)

    def format_input_for_classification_prompt(self, items):
        return '\n'.join([f"<ITEM_{i}>{item}</ITEM_{i}>" for i, item in enumerate(items)])

    def parse_classification_results(self, raw_results):
        results = raw_results.strip()
        results = results.split('<OUTPUT>')[1].split('</OUTPUT>')[0].strip().split('\n')

        final_results = []
        for i, result in enumerate(results):
            final_result = result.split(f'</CATEGORIES_{i}>')[0].split(f'<CATEGORIES_{i}>')[1]
            final_results.append(final_result.strip().split(';'))

        return final_results

    def classify(self, prompt_template, items, max_tokens_per_item=200):
        task_prompt = prompt_template.replace('<INSERT_ITEMS_HERE>', self.format_input_for_classification_prompt(items))
        raw_results = self.llm_client.classify(task_prompt, len(items), max_tokens_per_item)
        logger.info(f"Raw completion: {raw_results}")
        return self.parse_classification_results(raw_results)

    def classify_and_store_results(self, schema_id, items):
        # load prompt from schema
        schema = load_file_from_s3(self.output_bucket, f"{schema_id}.json")
        schema = json.loads(schema)
        prompt = schema['prompt']
        logger.info(f"Prompt for schema {schema['schema_name']} retrieved successfully")

        item_texts = [item['text'] for item in items]
        classification_results = self.classify(prompt, item_texts)

        if (classification_results is None or len(classification_results) == 0
                or len(classification_results) != len(items)):
            logger.info(f"Classification results: {classification_results}")
            raise PrestoBaseException(f"Not all items were classified successfully: input length {len(items)}, output length {len(classification_results)}", 502)

        final_results = [{'id': items[i]['id'], 'text': items[i]['text'], 'labels': classification_results[i]}
                         for i in range(len(items))]

        # filtering out the results that have out-of-schema labels
        # our of schema labels will not be included in the final results,
        # and items with no labels can be retried later by the user, indicated by an empty list for labels
        permitted_labels = [topic['topic'] for topic in schema['topics']] + ['Other', 'Unsure']
        for result in final_results:

            # log the items that had at least one out-of-schema label
            if not all([label in permitted_labels for label in result['labels']]):
                logger.error(f"Item {result['id']} had out-of-schema labels: {result['labels']}, permitted labels: {permitted_labels}")

            result['labels'] = [label for label in result['labels'] if label in permitted_labels]

        if not all([len(result['labels']) == 0 for result in final_results]):
            results_file_id = str(uuid.uuid4())
            upload_file_to_s3(self.output_bucket, f"{schema_id}/{results_file_id}.json", json.dumps(final_results))

        return final_results


    def schema_id_exists(self, schema_id):
        return file_exists_in_s3(self.output_bucket, f"{schema_id}.json")


    def process(self, message: Message) -> ClassyCatBatchClassificationResponse:
        # Example input:
        # {
        #     "model_name": "classycat__Model",
        #     "body": {
        #         "id": 1200,
        #         "parameters": {
        #             "event_type": "classify",
        #             "schema_id": "4a026b82-4a16-440d-aed7-bec07af12205",
        #             "items": [
        #                 {
        #                     "id": "11",
        #                     "text": "modi and bjp want to rule india by dividing people against each other"
        #                 }
        #             ]
        #         },
        #         "callback_url": "http://example.com?callback"
        #     }
        # }
        #
        # Example output:
        # {
        #     "body": {
        #         "id": 1200,
        #         "content_hash": null,
        #         "callback_url": "http://host.docker.internal:9888",
        #         "url": null,
        #         "text": null,
        #         "raw": {},
        #         "parameters": {
        #             "event_type": "classify",
        #             "schema_id": "12589852-4fff-430b-bf77-adad202d03ca",
        #             "items": [
        #                 {
        #                     "id": "11",
        #                     "text": "modi and bjp want to rule india by dividing people against each other"
        #                 }
        #             ]
        #         },
        #         "result": {
        #             "responseMessage": "success",
        #             "classification_results": [
        #                 {
        #                     "id": "11",
        #                     "text": "modi and bjp want to rule india by dividing people against each other",
        #                     "labels": [
        #                         "Politics",
        #                         "Communalism"
        #                     ]
        #                 }
        #             ]
        #         }
        #     },
        #     "model_name": "classycat.Model",
        #     "retry_count": 0
        # }

        # unpack parameters for classify
        batch_to_classify = message.body.parameters
        schema_id = batch_to_classify["schema_id"]
        items = batch_to_classify["items"]

        result = message.body.result

        if not self.schema_id_exists(schema_id):
            raise PrestoBaseException(f"Schema id {schema_id} cannot be found", 404)

        if len(items) > self.batch_size_limit:
            raise PrestoBaseException(f"Number of items exceeds batch size limit of {self.batch_size_limit}", 422)

        try:
            result.classification_results = self.classify_and_store_results(schema_id, items)
            result.responseMessage = "success"
            return result
        except Exception as e:
            logger.exception(f"Error classifying items: {e}")
            if isinstance(e, PrestoBaseException):
                raise e
            else:
                raise PrestoBaseException(f"Error classifying items: {e}", 500) from e


    @classmethod
    def validate_input(cls, data: Dict) -> None:
        """
        Validate input data. Must be implemented by all child "Model" classes.
        """
        if "schema_id" not in data["parameters"] or data["parameters"]["schema_id"] == "":
            raise PrestoBaseException("schema_id is required as input to classify", 422)

        if "items" not in data["parameters"] or len(data["parameters"]["items"]) == 0:
            raise PrestoBaseException("items are required as input to classify", 422)

        for item in data["parameters"]["items"]:
            if "id" not in item or item["id"] == "":
                raise PrestoBaseException("id is required for each item", 422)
            if "text" not in item or item["text"] == "":
                raise PrestoBaseException("text is required for each item", 422)

    @classmethod
    def parse_input_message(cls, data: Dict) -> Any:
        """
        Parse input into appropriate response instances.
        """
        event_type = data['parameters']['event_type']
        result_data = data.get('result', {})

        if event_type == 'classify':
            return ClassyCatBatchClassificationResponse(**result_data)
        else:
            logger.error(f"Unknown event type {event_type}")
            raise PrestoBaseException(f"Unknown event type {event_type}", 422)