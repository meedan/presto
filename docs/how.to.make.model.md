# How to make a presto model
## Your go-to guide, one-stop shop for writing your model in presto

A model in Presto is a (mostly) stateless Python class that has the following properties:
- Extends the `lib.model.model.Model` class
- `__init__()`: Overrides the default constructor method that initializes the model and its parameters.
from lib.model.classycat_classify:
```python
class Model(Model):
    def __init__(self):
        super().__init__()
        self.output_bucket = os.getenv("CLASSYCAT_OUTPUT_BUCKET")
        self.batch_size_limit = int(os.environ.get("CLASSYCAT_BATCH_SIZE_LIMIT"))
        llm_client_type = os.environ.get('CLASSYCAT_LLM_CLIENT_TYPE')
        llm_model_name = os.environ.get('CLASSYCAT_LLM_MODEL_NAME')
        self.llm_client = self.get_llm_client(llm_client_type, llm_model_name)
```

- `process()`: A method that processes the input data and returns the specific output of the specified predefined schema
This method is the meat of your model, and is supposed to statelessly process the input data and return the output data.
It's good practice to copy a standard input and output schema so that others can consume your model easily.
This method should return your own custom defined response classes, see ClassyCatBatchClassificationResponse for an example.
```python
def process(self, message: Message) -> ClassyCatBatchClassificationResponse:
    # Example input:
    # {
    #     "model_name": "classycat__Model",
    #     "body": {
    #         "id": 1200,
    #         "parameters": {
    #             "event_type": "classify",
    #             "schema_id": "4a026b82-4a16-440d-aed7-bec07af12205",
    #             "items": [
    #                 {
    #                     "id": "11",
    #                     "text": "modi and bjp want to rule india by dividing people against each other"
    #                 }
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
    #             "event_type": "classify",
    #             "schema_id": "12589852-4fff-430b-bf77-adad202d03ca",
    #             "items": [
    #                 {
    #                     "id": "11",
    #                     "text": "modi and bjp want to rule india by dividing people against each other"
    #                 }
    #             ]
    #         },
    #         "result": {
    #             "responseMessage": "success",
    #             "classification_results": [
    #                 {
    #                     "id": "11",
    #                     "text": "modi and bjp want to rule india by dividing people against each other",
    #                     "labels": [
    #                         "Politics",
    #                         "Communalism"
    #                     ]
    #                 }
    #             ]
    #         }
    #     },
    #     "model_name": "classycat.Model",
    #     "retry_count": 0
    # }

    # unpack parameters for classify
    batch_to_classify = message.body.parameters
    schema_id = batch_to_classify["schema_id"]
    items = batch_to_classify["items"]

    result = message.body.result

    if not self.schema_id_exists(schema_id):
        raise PrestoBaseException(f"Schema id {schema_id} cannot be found", 404)

    if len(items) > self.batch_size_limit:
        raise PrestoBaseException(f"Number of items exceeds batch size limit of {self.batch_size_limit}", 422)

    try:
        result.classification_results = self.classify_and_store_results(schema_id, items)
        result.responseMessage = "success"
        return result
    except Exception as e:
        logger.exception(f"Error classifying items: {e}")
        if isinstance(e, PrestoBaseException):
            raise e
        else:
            raise PrestoBaseException(f"Error classifying items: {e}", 500) from e
```
- In case of errors, raise a `PrestoBaseException` with the appropriate error message and http status code, as seen above.
feel free to extend this class and implement more sophisticated error handling for your usecase if needed.
- `validate_input()`: A method that validates the input data and raises an exception if the input is invalid.
```python
@classmethod
def validate_input(cls, data: Dict) -> None:
    """
    Validate input data. Must be implemented by all child "Model" classes.
    """
    if "schema_id" not in data["parameters"] or data["parameters"]["schema_id"] == "":
        raise PrestoBaseException("schema_id is required as input to classify", 422)

    if "items" not in data["parameters"] or len(data["parameters"]["items"]) == 0:
        raise PrestoBaseException("items are required as input to classify", 422)

    for item in data["parameters"]["items"]:
        if "id" not in item or item["id"] == "":
            raise PrestoBaseException("id is required for each item", 422)
        if "text" not in item or item["text"] == "":
            raise PrestoBaseException("text is required for each item", 422)
```
- `parse_input_message()`: generates the right result/response type from the raw input body:
```python
@classmethod
def parse_input_message(cls, data: Dict) -> Any:
    """
    Parse input into appropriate response instances.
    """
    event_type = data['parameters']['event_type']
    result_data = data.get('result', {})

    if event_type == 'classify':
        return ClassyCatBatchClassificationResponse(**result_data)
    else:
        logger.error(f"Unknown event type {event_type}")
        raise PrestoBaseException(f"Unknown event type {event_type}", 422)
```
- Your own custom defined response classes, ideally defined inside the model file or as a separate file if too complex. 
see `ClassyCatBatchClassificationResponse` for an example:
```python
class ClassyCatResponse(BaseModel):
    responseMessage: Optional[str] = None

class ClassyCatBatchClassificationResponse(ClassyCatResponse):
    classification_results: Optional[List[dict]] = []
```