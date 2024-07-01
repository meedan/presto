import os
import json
from lib.logger import logger
from lib.model.model import Model
from lib.s3 import load_file_from_s3, file_exists_in_s3
from lib.schemas import ClassyCatSchema


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


    def process(self, schema_lookup_event: ClassyCatSchema) -> ClassyCatSchema:
        # check if schema with the name exists, and if so return the id
        schema_name = schema_lookup_event.schema_name

        if not self.schema_name_exists(schema_name):
            schema_lookup_event.text = f"Schema name {schema_name} does not exist"
            return schema_lookup_event

        logger.debug(f"located schema_name record for '{schema_name}'")

        try:
            schema_lookup_event.schema_id = self.look_up_schema_id_by_name(schema_name)
            schema_lookup_event.text = "success"
            return schema_lookup_event
        except Exception as e:
            logger.error(f"Error looking up schema name {schema_name}: {e}")
            schema_lookup_event.text = f"Error looking up schema name {schema_name}: {e}"
            return schema_lookup_event