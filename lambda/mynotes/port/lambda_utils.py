import functools
import json
import jsons
from typing import Dict, Optional, Any
import base64

def get_path_parameter(event, param_name: str, default_value: str = "") -> Optional[str]:
    """Returns the value for the specified path parameter or the 'default_value' if not found
    
    Args:
        event: the AWS Lambda event (usually Application Gateway event)
        param_name: the name of the path parameter
        default_value: the default value for the parameter

    Returns:
        the value in the event object of the specified path parameter
    """
    map = event.get("pathParameters")
    if map:
        return map.get(param_name, default_value)

    return default_value

def get_json_body(event) -> Optional[Dict[str, Any]]:
    """Return the body as JSON object, if present; otherwise it will return None
    
    Args:
        event: the AWS Lambda event object

    Returns:
        a dictionary containing the deserialized JSON content included in the body section
    
    """
    body = event.get("body")
    is_base64_encoded = event.get("isBase64Encoded")

    if body:
        if is_base64_encoded:
            body = base64.b64decode(body)

        return json.loads(body)
    return None

def to_json_response(object_body: Any, http_status_code: int = 200, headers = None) -> Dict[str, Any]:
    """Wraps the inputs into an object that can be returned as part of AWS Lambda's execution using 
    the content type 'application/json'

    Args:
        object_body: the body that will be serialized into a JSON string
        http_status_code: the HTTP status code that will be associated with this response
        headers: any additional header (you can override the default content type using this)

    Returns:
        a wrapper dict that can be used as return value in AWS Lambda execution
    """
    json_response = {
        "statusCode": http_status_code,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": jsons.dumps(object_body)
    }

    if headers:
        json_response["headers"].update(headers)
    
    return json_response

def with_cors_headers(wrapped_function) -> Dict[str, Any]:
    @functools.wraps(wrapped_function)
    def apply_cors_headers(*args, **kwargs) -> Dict[str, Any]:
        lambda_response = wrapped_function(*args, **kwargs)
        if not "headers" in lambda_response:
            lambda_response["headers"] = {}
        lambda_response["headers"]["Access-Control-Allow-Origin"] = "*"
        lambda_response["headers"]["Access-Control-Allow-Credentials"] = True

        return lambda_response

    return apply_cors_headers