import os
import json
from lib.logger import logger
from lib.model.model import Model
from lib.s3 import load_file_from_s3


class Model(Model):
    def __init__(self):
        """
        Set some basic constants during operation, create local folder for tmk workspace.
        """
        self.schemas_bucket = os.getenv("CLASSYCAT_OUTPUT_BUCKET")


    def look_up_schema_id_by_name(self, schema_name):
        try:
            object = load_file_from_s3(self.schemas_bucket, f"{schema_name}.json")
            contents = json.loads(object)
            return contents["schema_id"]
        except Exception as e:
            logger.error(f"Error looking up schema name {schema_name}: {e}")
            return None


    def process(self):
        # check if schema with the name exists, and if so return the id
        schema_name = event["schema_name"]
        if not schema_name_exists(schema_name, s3_client, output_bucket):
            return {
                "statusCode": 404,  # TODO: somehow these are not getting turned into http status codes
                "body": {"message": f"Schema name {schema_name} does not exist"},
            }
        logger.debug(f"located schema_name record for '{schema_name}'")
        schema_id = get_schema_id_from_name(schema_name, s3_client, output_bucket)
        return {"statusCode": 200, "body": {"schema_id": schema_id}}