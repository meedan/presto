import os
import json
from lib.logger import logger
from lib.model.model import Model
from lib.s3 import load_file_from_s3, file_exists_in_s3
from lib.schemas import GenericItem


class Model(Model):
    def __init__(self):
        """
        Set some basic constants during operation, create local folder for tmk workspace.
        """
        self.schemas_bucket = os.getenv("CLASSYCAT_OUTPUT_BUCKET")


    def schema_name_exists(self, schema_name):
        return file_exists_in_s3(self.output_bucket, f"{schema_name}.json")


    def look_up_schema_id_by_name(self, schema_name):
        object = load_file_from_s3(self.schemas_bucket, f"{schema_name}.json")
        contents = json.loads(object)
        return contents["schema_id"]


    def process(self, schema_lookup_event: GenericItem) -> GenericItem:
        # check if schema with the name exists, and if so return the id
        schema_name = schema_lookup_event.parameters["schema_name"]

        result = GenericItem()

        if not self.schema_name_exists(schema_name):
            result.text = f"Schema name {schema_name} does not exist"
            return result

        logger.debug(f"located schema_name record for '{schema_name}'")

        try:
            result.id = self.look_up_schema_id_by_name(schema_name)
            result.text = "success"
            return result
        except Exception as e:
            logger.error(f"Error looking up schema name {schema_name}: {e}")
            result.text = f"Error looking up schema name {schema_name}: {e}"
            return result