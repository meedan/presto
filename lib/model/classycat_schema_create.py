import os
import json
import uuid
from lib.s3 import upload_file_to_s3
from lib.logger import logger
from lib.model.model import Model


class Model(Model):
    def __init__(self):
        """
        Set some basic constants during operation, create local folder for tmk workspace.
        """
        self.output_bucket = os.getenv("CLASSYCAT_OUTPUT_BUCKET")
        self.base_prompt = (
            "You are given a list of items in {languages} to classify. "
            "Each item can fit into one or multiple categories. "
            "If an item does not belong to any of the listed categories in the taxonomy, classify it as ‘Other’. "
            "If you are an unsure about an item, classify it as ‘Unsure’. "
            "If an item belongs to multiple categories, separate the categories with a ';'. "
            "The input and output conform to the following format:\n"
            "<INPUT>\n<ITEM_0>...</ITEM_0>\n<ITEM_1>...</ITEM_1>\n...\n<ITEM_N>...</ITEM_N>\n</INPUT>\n"
            "<OUTPUT>\n<CATEGORIES_0>...</CATEGORIES_0>\n<CATEGORIES_1>...</CATEGORIES_1>\n...\n<CATEGORIES_N>...</CATEGORIES_N>\n</OUTPUT>\n\n"
            "Here is the {schema_name} taxonomy with examples for each category included:\n{categories}\n\n"
            "Classify the following items:\n<INPUT>\n<INSERT_ITEMS_HERE>\n</INPUT>"
        )


    def create_schema(self, schema_name, topics, examples, languages): # todo add type to arguments
        schema_id = str(uuid.uuid4())
        schema_filename = f"{schema_id}.json"
        schema_id_mapping_filename = f"{schema_name}.json"

        schema = {
            "schema_id": schema_id,
            "schema_name": schema_name,
            "topics": topics,
            "examples": examples,
            "languages": languages,
        }

        schema["prompt"] = self.generate_prompt_from_schema(schema)

        upload_file_to_s3(self.output_bucket, schema_filename, json.dumps(schema))
        # s3_client.put_object(
        #     Bucket=output_bucket, Key=schema_filename, Body=json.dumps(schema)
        # )

        upload_file_to_s3(self.output_bucket, schema_id_mapping_filename, json.dumps({"schema_id": schema_id}))
        # s3_client.put_object(
        #     Bucket=output_bucket,
        #     Key=schema_id_mapping_filename,
        #     Body=json.dumps({"schema_id": schema_id}),
        # )
        logger.info(f"Schema {schema_name} created with id {schema_id}")

        return schema_id


    def generate_prompt_from_schema(self, schema):
        topics = schema["topics"]
        examples = schema["examples"]
        languages = (
            " and ".join(schema["languages"])
            if len(schema["languages"]) <= 2
            else ", ".join(schema["languages"][:-1]) + f", and {schema['languages'][-1]}"
        )
        prompt_categories = [
            "<TAXONOMY>",
            f"<TITLE>{schema['schema_name']}</TITLE>",
            "<TOPICS>",
        ]

        for i, topic in enumerate(topics):
            prompt_categories.append(
                f"<TOPIC_{i}><TITLE>{topic['topic']}</TITLE><DESCRIPTION>{topic['description']}</DESCRIPTION></TOPIC_{i}>"
            )

        prompt_categories.append("</TOPICS>")

        prompt_categories.append("<EXAMPLES>")
        prompt_categories.append("<INPUT>")

        for i, example in enumerate(examples):
            prompt_categories.append(f"<ITEM_{i}>{example['text']}</ITEM_{i}>")

        prompt_categories.append("</INPUT>")
        prompt_categories.append("<OUTPUT>")

        for i, example in enumerate(examples):
            prompt_categories.append(
                f"<CATEGORIES_{i}>{';'.join(example['labels'])}</CATEGORIES_{i}>"
            )

        prompt_categories.append("</OUTPUT>")
        prompt_categories.append("</EXAMPLES>")

        prompt_categories.append("</TAXONOMY>")

        return self.base_prompt.format(
            categories="\n".join(prompt_categories),
            languages=languages,
            schema_name=schema["schema_name"],
        )


    def process(self):
        # unpack parameters for create_schema
        schema_name = event["schema_name"]
        # topics is a list of dictionaries:
        # [
        # {topic: 'topic1', description: 'topic 1 is ...'},
        # {topic: 'topic2', description: 'topic 2 is ...'}
        # ]
        topics = event["topics"]
        # examples is a list of dictionaries:
        # [{'text': 'example 1', 'labels': ['label1', 'label2']}, {'text': 'example 2', 'labels': ['label3', 'label4']}]
        # there should be at least one example per topic
        examples = event["examples"]
        languages = event["languages"]  # ['English', 'Spanish']

        if schema_name_exists(schema_name, s3_client, output_bucket):
            return {
                "statusCode": 400,
                "body": {"message": f"Schema name {schema_name} already exists"},
            }

        try:
            verify_schema_parameters(schema_name, topics, examples, languages)
        except Exception as e:
            logger.exception(f"Error verifying schema parameters: {e}")
            return {
                "statusCode": 400,
                "body": {
                    "message": f"Error verifying schema parameters. Stack trace: {e}"
                },
            }

        try:
            schema_id = create_schema(
                schema_name, topics, examples, languages, s3_client, output_bucket
            )
            return {"statusCode": 200, "body": {"schema_id": schema_id}}
        except Exception as e:
            logger.exception(f"Error creating schema: {e}")
            return {
                "statusCode": 500,
                "body": {"message": f"Error creating schema. Stack trace: {e}"},
            }


    def verify_schema_parameters(self, schema_name, topics, examples, languages): #todo

        if not schema_name or not isinstance(schema_name, str) or len(schema_name) == 0:
            raise ValueError("schema_name is invalid. It must be a non-empty string")

        if not topics or not isinstance(topics, list) or len(topics) == 0:
            raise ValueError(
                "topics is invalid. It must be a non-empty list of dictionaries"
            )

        for topic in topics:
            if (
                "description" not in topic
                or not isinstance(topic["description"], str)
                or len(topic["description"]) == 0
            ):
                raise ValueError(
                    f"Description for topic {topic['topic']} is invalid. It must be a non-empty string"
                )

        if not examples or not isinstance(examples, list) or len(examples) == 0:
            raise ValueError(
                "examples is invalid. It must be a non-empty list of dictionaries containing 'text' and 'labels' keys"
            )

        if not languages or not isinstance(languages, list) or len(languages) == 0:
            raise ValueError(
                "languages is invalid. It must be a non-empty string list of languages"
            )


    def schema_name_exists(self, schema_name, s3_client, output_bucket): # todo
        try:
            s3_client.head_object(Bucket=output_bucket, Key=f"{schema_name}.json")
            return True
        except:
            return False


def schema_id_exists(schema_id, s3_client, output_bucket):
    try:
        s3_client.head_object(Bucket=output_bucket, Key=f"{schema_id}.json")
        return True
    except:
        return False



