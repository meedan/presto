from lib.logger import logger
from lib.model.model import Model
from lib.schemas import Message, ClassyCatResponse
from lib.model.classycat_classify import Model as ClassifyModel
from lib.model.classycat_schema_create import Model as ClassyCatSchemaCreateModel
from lib.model.classycat_schema_lookup import Model as ClassyCatSchemaLookupModel


class Model(Model):
    def __init__(self):
        super().__init__()

    def process(self, message: Message) -> ClassyCatResponse:
        event_type = message.body.parameters["event_type"]
        if event_type == 'classify':
            return ClassifyModel().process(message)
        elif event_type == 'schema_lookup':
            return ClassyCatSchemaLookupModel().process(message)
        elif event_type == 'schema_create':
            return ClassyCatSchemaCreateModel().process(message)
        else:
            logger.error(f"Unknown event type {event_type}")
            message.body.result.responseMessage = f"Unknown event type {event_type}"
            return message.body.result