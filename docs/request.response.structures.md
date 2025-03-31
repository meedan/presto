# Expected incoming request and outgoing response datastructures for Presto models

Presto models should use these structures to ensure that tools that consume the data can access in a consistant way across models

Details of specific model's input and response formats are usually in the `<model_name>_response.py` files.  i.e. `classycat_response.py`

## Incoming requests to presto

General design

* Models that don't handle requests in parallel need to implement batch format (but can give errors if they recieve more than 1 item)
* "top level" elements in the payload (outermost dictionary keys) are processed and controlled by the Presto system
* Elements inside parameters, and inside individual input items are passed through to the model
* From the perspective of the calling service, all the of the items in a single batch call must be dispatched to the same Presto model service.  (don't mix items for paraphrase and classycat it the same call)
* Any parameter settings to the model must apply to all items in batch
* Request itself needs a unique id, (and this is different than the id of the content)
* There is single callback URL for entire batch
* Some items need additional input parameters per item (i.e. “language” for YAKE), Presto just passes thes through
* The input structure will be returned in the response by the presto system, so individual models don't have to copy inputs to outputs. As long as ..
* All input_items must include an `id` element that can be used as a reference from the output items to match up to input parameters

Example PROPOSED input object structure (classycat)
```
{
    request_id:122,              
    model_name:"classycat__Model",       # model to be used 
    model_parameters: {
        "event_type": "classify",
        "schema_id": "4a026b82-4a16-440d-aed7-bec07af12205",
    },
    input_items:[
        {
            id:"11",
            text:"this is some text to classify", 
            workspace_id:"timpani_meedan", 
            target_state:"classified", 
        },
        {
            id:"12",
            text:"Este é um texto para classificar", 
            workspace_id:"timpani_meedan", 
            target_state:"classified", 
        },
    ],
    callback_url: "http://conductor/batch_reply/",
}

```
Example PROPOSED input object structure (YAKE)
{
    request_id:422,              
    model_name:"yake_keywords__Model",       # model to be used 
    model_parameters: {
        "max_ngram_size":3,
        "deduplication_threshold":0.25
    },
    input_items:[
        {
            id:"11",
            text:"this is some text to classify", 
            workspace_id:"timpani_meedan", 
            target_state:"keyworded", 
            language:"en",

        },
    ],
    callback_url: "http://conductor/batch_reply/",
}


Example PROPOSED input object structure (paraphrase-multilingual)


Example 'curl' command (put here after implementation)


## Outgoing requests from presto

* The outgoing reponse request includes the payloads and parameters from the incoming request
* items in the response must include their id, so that the caller can match and lookup individual-level properties from incoming request. 
* status code is present at top level so it can be checked to know how to parse the rest of the payload (error etc)

Example PROPOSED output structure
```
{
    request_id:122,              
    model_name:"classycat__Model",       # model to be used 
    model_parameters: {
        "event_type": "classify",
        "schema_id": "4a026b82-4a16-440d-aed7-bec07af12205",
    },
    input_items:[
        {
            id:"11",
            text:"this is some text to classify", 
            workspace_id:"timpani_meedan", 
            target_state:"classified", 
            language:"en"

        },
        {
            id:"12",
            text:"Este é um texto para classificar", 
            workspace_id:"timpani_meedan", 
            target_state:"classified", 
            language:"pt"
        },
    ],
    callback_url: "http://conductor/batch_reply/",

    # elements below here are added in response

    "retry_count": 0
    "status_code": 200
    "status_message":"success"
    "results": [
            {
                "id": "11",     #  this id can be used to look up params from input
                "text": "this is some text to classify",   # text is redundant with input, but helpful for model-level debugging
                "labels": [
                    "Testing",
                    "Classification"
                ]
            },
            {
                "id": "12",
                "text": "Este é um texto para classificar",
                "labels": [
                    "Testing",
                    "Classification"
                ]
            }
        ]
    },

    ```

Example PROPOSED output object structure (YAKE)
{
    request_id:422,              
    model_name:"yake_keywords__Model",       # model to be used 
    model_parameters: {
        "max_ngram_size":3,
        "deduplication_threshold":0.25
    },
    input_items:[
        {
            id:"11",
            text:"this is some text to classify", 
            workspace_id:"timpani_meedan", 
            target_state:"keyworded", 
            language:"en",

        },
    ],
    callback_url: "http://conductor/batch_reply/",
    "retry_count": 0
    "status_code": 200
    "status_message":"success"
    "results": [
            {
                "id": "11",     #  this id can be used to look up params from input
                "text": "this is some text to classify",  
                "keywords": [
                    ["lookup",0.0020211625251083634],
                    ["params",0.0020211625251083634]
                ]
            },
           
        ]
}

# Error response structures

"status_code": 403
"status_message":"unable to access model"

## Not covered
per item errors?