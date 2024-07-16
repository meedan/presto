import os
import json
import uuid
from lib.s3 import upload_file_to_s3, file_exists_in_s3
from lib.logger import logger
from lib.model.model import Model
from lib.schemas import Message, ClassyCatSchemaResponse


class Model(Model):
    def __init__(self):
        super().__init__()
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


    def create_schema(self, schema_name, topics, examples, languages):
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
        upload_file_to_s3(self.output_bucket, schema_id_mapping_filename, json.dumps({"schema_id": schema_id}))

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


    def process(self, message: Message) -> ClassyCatSchemaResponse:
        # example input:
        # {
        #     "model_name": "classycat__Model",
        #     "body": {
        #         "id": 1200,
        #         "parameters": {
        #             "event_type": "schema_create",
        #             "schema_name": "2024 Indian Election Test",
        #             "topics": [
        #                 {
        #                     "topic": "Politics",
        #                     "description": "This topic includes political claims, attacks on leaders and parties, and general political commentary."
        #                 },
        #                 {
        #                     "topic": "Communalism",
        #                     "description": "This topic covers attack on religious minorities, statements on religious freedom and polarization."
        #                 }
        #             ],
        #             "examples": [
        #                 {
        #                     "text": "Congress Manifesto is horrible. Never seen such a dangerous manifesto in my life. It's like vision 2047 document of PFI\n\nCheck these points of manifesto\n\n1. Will bring back triple talak (Muslim personal law)\n2. Reservation to Muslim in govt n private jobs (Implement Sachchar committee report)\n3. Support Love Jihad (right to love)\n4. Support Burqa in school (right to dress)\n5. End majoritarianism (Hinduism)\n6. Ban bulldozer action\n7. Support Gaza (Hamas)\n8. Legalise Same Sex Marriage, gender fluidity, trans movement\n9. Increase Muslim judges in judiciary\n10. Communal violence bill (will stop mob lynching)\n11. Legalise beef (right to eat everything)\n12. Separate loan intrest for Muslims\n13. Allow treason (No sedition)\n\nAll those Hindu who are thinking to vote Indi Alliance, NOTA or independent. Read this and think.\n",
        #                     "labels": [
        #                         "Politics",
        #                         "Communalism"
        #                     ]
        #                 }
        #             ],
        #             "languages": [
        #                 "English",
        #                 "Hindi",
        #                 "Telugu",
        #                 "Malayalam"
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
        #             "event_type": "schema_create",
        #             "schema_name": "2024 Indian Election Test 2",
        #             "topics": [
        #                 {
        #                     "topic": "Politics",
        #                     "description": "This topic includes political claims, attacks on leaders and parties, and general political commentary."
        #                 },
        #                 {
        #                     "topic": "Communalism",
        #                     "description": "This topic covers attack on religious minorities, statements on religious freedom and polarization."
        #                 }
        #             ],
        #             "examples": [
        #                 {
        #                     "text": "Congress Manifesto is horrible. Never seen such a dangerous manifesto in my life. It's like vision 2047 document of PFI\n\nCheck these points of manifesto\n\n1. Will bring back triple talak (Muslim personal law)\n2. Reservation to Muslim in govt n private jobs (Implement Sachchar committee report)\n3. Support Love Jihad (right to love)\n4. Support Burqa in school (right to dress)\n5. End majoritarianism (Hinduism)\n6. Ban bulldozer action\n7. Support Gaza (Hamas)\n8. Legalise Same Sex Marriage, gender fluidity, trans movement\n9. Increase Muslim judges in judiciary\n10. Communal violence bill (will stop mob lynching)\n11. Legalise beef (right to eat everything)\n12. Separate loan intrest for Muslims\n13. Allow treason (No sedition)\n\nAll those Hindu who are thinking to vote Indi Alliance, NOTA or independent. Read this and think.\n",
        #                     "labels": [
        #                         "Politics",
        #                         "Communalism"
        #                     ]
        #                 }
        #             ],
        #             "languages": [
        #                 "English",
        #                 "Hindi",
        #                 "Telugu",
        #                 "Malayalam"
        #             ]
        #         },
        #         "result": {
        #             "responseMessage": "success",
        #             "schema_id": "e6729bb9-2491-47dc-824d-828d929ebcd2"
        #         }
        #     },
        #     "model_name": "classycat.Model",
        #     "retry_count": 0
        # }

        # unpack parameters for create_schema
        schema_specs = message.body.parameters

        schema_name = schema_specs["schema_name"]
        topics = schema_specs["topics"]
        examples = schema_specs["examples"]
        languages = schema_specs["languages"]  # ['English', 'Spanish']

        result = message.body.result

        if self.schema_name_exists(schema_name):
            result.responseMessage = f"Schema name {schema_name} already exists"
            return result

        try:
            self.verify_schema_parameters(schema_name, topics, examples, languages)
        except Exception as e:
            logger.exception(f"Error verifying schema parameters: {e}")
            result.responseMessage = f"Error verifying schema parameters. Stack trace: {e}"
            return result

        try:
            result.schema_id = self.create_schema(schema_name, topics, examples, languages)
            result.responseMessage = 'success'
            return result
        except Exception as e:
            logger.exception(f"Error creating schema: {e}")
            result.responseMessage = f"Error creating schema. Stack trace: {e}"
            return result


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


    def schema_name_exists(self, schema_name):
        return file_exists_in_s3(self.output_bucket, f"{schema_name}.json")
