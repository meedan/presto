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
            raise Exception(f"Unknown client type: {client_type}")

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
            raise Exception(f"Not all items were classified successfully: "
                            f"input length {len(items)}, output length {len(classification_results)}")
        # TODO: validate response label against schema https://meedan.atlassian.net/browse/CV2-4801
        final_results = [{'id': items[i]['id'], 'text': items[i]['text'], 'labels': classification_results[i]}
                         for i in range(len(items))]
        results_file_id = str(uuid.uuid4())
        upload_file_to_s3(self.output_bucket, f"{schema_id}/{results_file_id}.json", json.dumps(final_results))

        return final_results


    def schema_id_exists(self, schema_id):
        return file_exists_in_s3(self.output_bucket, f"{schema_id}.json")


    def process(self, message: Message) -> ClassyCatBatchClassificationResponse:
        # unpack parameters for classify
        batch_to_classify = message.body.parameters
        schema_id = batch_to_classify["schema_id"]
        items = batch_to_classify["items"]

        result = message.body.result

        if not self.schema_id_exists(schema_id):
            result.responseMessage = f"Schema id {schema_id} cannot be found"
            return result

        if len(items) > self.batch_size_limit:
            result.responseMessage = f"Number of items exceeds batch size limit of {self.batch_size_limit}"
            return result

        try:
            result.classification_results = self.classify_and_store_results(schema_id, items)
            result.responseMessage = "success"
            return result
        except Exception as e:
            logger.exception(f"Error classifying items: {e}")
            result.responseMessage = f"Error classifying items: {e}"
            return result
