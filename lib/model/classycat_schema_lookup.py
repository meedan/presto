import os
import json
from lib.logger import logger
from lib.model.model import Model
from lib.s3 import load_file_from_s3, file_exists_in_s3
from lib.schemas import Message, ClassyCatSchemaResponse


class Model(Model):
    def __init__(self):
        super().__init__()
        self.schemas_bucket = os.getenv("CLASSYCAT_OUTPUT_BUCKET")


    def schema_name_exists(self, schema_name):
        return file_exists_in_s3(self.schemas_bucket, f"{schema_name}.json")


    def look_up_schema_id_by_name(self, schema_name):
        object = load_file_from_s3(self.schemas_bucket, f"{schema_name}.json")
        contents = json.loads(object)
        return contents["schema_id"]


    def process(self, message: Message) -> ClassyCatSchemaResponse:
        # Example input:
        # {
        #     "model_name": "classycat__Model",
        #     "body": {
        #         "callback_url": "http://example.com?callback",
        #         "id": 1200,
        #         "parameters": {
        #             "event_type": "schema_lookup",
        #             "schema_name": "2024 Indian Election Test"
        #         }
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
        #             "event_type": "schema_lookup",
        #             "schema_name": "2024 Indian Election Test"
        #         },
        #         "result": {
        #             "responseMessage": "success",
        #             "schema_id": "12589852-4fff-430b-bf77-adad202d03ca"
        #         }
        #     },
        #     "model_name": "classycat.Model",
        #     "retry_count": 0
        # }

        # check if schema with the name exists, and if so return the id
        schema_name = message.body.parameters["schema_name"]
        result = message.body.result

        if not self.schema_name_exists(schema_name):
            result.responseMessage = f"Schema name {schema_name} does not exist"
            return result

        logger.debug(f"located schema_name record for '{schema_name}'")

        try:
            result.schema_id = self.look_up_schema_id_by_name(schema_name)
            result.responseMessage = "success"
            return result
        except Exception as e:
            logger.error(f"Error looking up schema name {schema_name}: {e}")
            result.responseMessage = f"Error looking up schema name {schema_name}: {e}"
            return result