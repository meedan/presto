from typing import Union, Dict, Any
from lib.logger import logger
from lib.model.model import Model
from lib.schemas import Message, ClassyCatSchemaResponse, ClassyCatBatchClassificationResponse
from lib.model.classycat_classify import Model as ClassifyModel
from lib.model.classycat_schema_create import Model as ClassyCatSchemaCreateModel
from lib.model.classycat_schema_lookup import Model as ClassyCatSchemaLookupModel
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
        pass

    @classmethod
    def parse_input_message(cls, data: Dict) -> Any:
        """
        Validate input data. Must be implemented by all child "Model" classes.
        """
        return None
