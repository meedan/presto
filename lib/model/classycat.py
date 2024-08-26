from typing import Union, Dict, Any
from lib.logger import logger
from lib.model.model import Model
from lib.schemas import Message
from lib.model.classycat_classify import Model as ClassifyModel
from lib.model.classycat_schema_create import Model as ClassyCatSchemaCreateModel
from lib.model.classycat_schema_lookup import Model as ClassyCatSchemaLookupModel
from lib.model.classycat_response import ClassyCatSchemaResponse, ClassyCatBatchClassificationResponse
from lib.base_exception import PrestoBaseException


class Model(Model):
    def __init__(self):
        super().__init__()

    def process(self, message: Message) -> Union[ClassyCatSchemaResponse, ClassyCatBatchClassificationResponse]:
        event_type = message.body.parameters["event_type"]
        if event_type == 'classify':
            return ClassifyModel().process(message)
        elif event_type == 'schema_lookup':
            return ClassyCatSchemaLookupModel().process(message)
        elif event_type == 'schema_create':
            return ClassyCatSchemaCreateModel().process(message)
        else:
            logger.error(f"Unknown event type {event_type}")
            raise PrestoBaseException(f"Unknown event type {event_type}", 422)

    @classmethod
    def validate_input(cls, data: Dict) -> None:
        """
        Validate input data. Must be implemented by all child "Model" classes.
        """
        event_type = data['parameters']['event_type']

        if event_type == 'classify':
            ClassifyModel.validate_input(data)
        elif event_type == 'schema_lookup':
            ClassyCatSchemaLookupModel.validate_input(data)
        elif event_type == 'schema_create':
            ClassyCatSchemaCreateModel.validate_input(data)
        else:
            logger.error(f"Unknown event type {event_type}")
            raise PrestoBaseException(f"Unknown event type {event_type}", 422)

    @classmethod
    def parse_input_message(cls, data: Dict) -> Any:
        """
        Parse input into appropriate response instances.
        """
        event_type = data['parameters']['event_type']

        if event_type == 'classify':
            result_instance_class = ClassifyModel
        elif event_type == 'schema_lookup':
            result_instance_class = ClassyCatSchemaLookupModel
        elif event_type == 'schema_create':
            result_instance_class = ClassyCatSchemaCreateModel

        else:
            logger.error(f"Unknown event type {event_type}")
            raise PrestoBaseException(f"Unknown event type {event_type}", 422)

        return result_instance_class.parse_input_message(data)
